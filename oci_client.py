"""
Oracle Cloud Infrastructure Client for VM creation.
Handles instance creation with proper error handling for capacity issues.
"""

import oci
from config import Config


class OCIClient:
    """Oracle Cloud Infrastructure client wrapper."""
    
    # Known error messages for out of capacity
    CAPACITY_ERROR_MESSAGES = [
        "Out of host capacity",
        "Out of capacity",
        "capacity",
        "InternalError",
        "LimitExceeded",
    ]
    
    def __init__(self, config: Config):
        self.config = config
        self.compute_client = oci.core.ComputeClient(config.get_oci_config())
        self.virtual_network_client = oci.core.VirtualNetworkClient(config.get_oci_config())
    
    def create_instance(self) -> dict:
        """
        Attempt to create a VM.Standard.A1.Flex instance.
        
        Returns:
            dict with keys:
            - success: bool
            - message: str
            - instance: instance details if successful
            - is_capacity_error: bool (True if failed due to capacity)
        """
        try:
            # Shape configuration for flexible ARM instance
            shape_config = oci.core.models.LaunchInstanceShapeConfigDetails(
                ocpus=float(self.config.ocpus),
                memory_in_gbs=float(self.config.memory_gb)
            )
            
            # Source details (boot volume from image)
            source_details = oci.core.models.InstanceSourceViaImageDetails(
                source_type="image",
                image_id=self.config.image_ocid,
                boot_volume_size_in_gbs=50  # 50GB boot volume (free tier limit)
            )
            
            # VNIC (network interface) details
            create_vnic_details = oci.core.models.CreateVnicDetails(
                subnet_id=self.config.subnet_ocid,
                assign_public_ip=True
            )
            
            # SSH key metadata
            metadata = {
                "ssh_authorized_keys": self.config.ssh_public_key
            }
            
            # Launch instance details
            launch_details = oci.core.models.LaunchInstanceDetails(
                compartment_id=self.config.compartment_ocid,
                availability_domain=self.config.availability_domain,
                shape="VM.Standard.A1.Flex",
                shape_config=shape_config,
                source_details=source_details,
                create_vnic_details=create_vnic_details,
                display_name=self.config.instance_name,
                metadata=metadata
            )
            
            # Attempt to launch the instance
            response = self.compute_client.launch_instance(launch_details)
            instance = response.data
            
            # Get public IP (may take a moment to be assigned)
            public_ip = self._get_public_ip(instance.id)
            
            return {
                "success": True,
                "message": "Instance created successfully!",
                "instance": {
                    "id": instance.id,
                    "name": instance.display_name,
                    "shape": instance.shape,
                    "region": self.config.oci_region,
                    "availability_domain": instance.availability_domain,
                    "public_ip": public_ip,
                    "lifecycle_state": instance.lifecycle_state,
                },
                "is_capacity_error": False
            }
            
        except oci.exceptions.ServiceError as e:
            is_capacity = self._is_capacity_error(str(e))
            return {
                "success": False,
                "message": str(e.message),
                "instance": None,
                "is_capacity_error": is_capacity
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "instance": None,
                "is_capacity_error": False
            }
    
    def _is_capacity_error(self, error_message: str) -> bool:
        """Check if the error is related to capacity issues."""
        error_lower = error_message.lower()
        return any(msg.lower() in error_lower for msg in self.CAPACITY_ERROR_MESSAGES)
    
    def _get_public_ip(self, instance_id: str) -> str:
        """Get the public IP address of an instance."""
        try:
            # Wait a moment for VNIC to be attached
            import time
            time.sleep(5)
            
            # List VNIC attachments for the instance
            vnic_attachments = self.compute_client.list_vnic_attachments(
                compartment_id=self.config.compartment_ocid,
                instance_id=instance_id
            ).data
            
            if vnic_attachments:
                vnic = self.virtual_network_client.get_vnic(
                    vnic_attachments[0].vnic_id
                ).data
                return vnic.public_ip or "Not yet assigned"
            
            return "Not yet assigned"
        except Exception:
            return "Unable to retrieve"
    
    def validate_credentials(self) -> bool:
        """Validate OCI credentials by making a simple API call."""
        try:
            # Try to list availability domains (simple read operation)
            identity_client = oci.identity.IdentityClient(self.config.get_oci_config())
            identity_client.list_availability_domains(self.config.oci_tenancy_ocid)
            print("✅ OCI credentials validated successfully")
            return True
        except oci.exceptions.ServiceError as e:
            print(f"❌ OCI credential validation failed: {e.message}")
            return False
        except Exception as e:
            print(f"❌ OCI credential validation failed: {e}")
            return False


if __name__ == "__main__":
    # Test OCI client
    try:
        config = Config()
        client = OCIClient(config)
        client.validate_credentials()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
