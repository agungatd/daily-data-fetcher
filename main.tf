terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.2" # Use appropriate version
    }
  }
  # Optional: Backend configuration (e.g., S3 for remote state) would go here
  # in a real project, but we'll use local state for this tutorial.
}

# This is a PLACEHOLDER resource.
# In a real data pipeline, you would define resources like:
# - aws_s3_bucket / google_storage_bucket (for storing output data)
# - aws_db_instance / google_sql_database_instance (if loading to a DB)
# - aws_ec2_instance / google_compute_instance (if running on a VM)
# - aws_ecs_task_definition / google_cloud_run_service (for container execution)
# - etc.
resource "local_file" "pipeline_marker" {
  content  = "This file indicates that the Terraform infrastructure setup for the simple-data-pipeline was run at ${timestamp()}."
  filename = "${path.module}/output/terraform_marker.txt" # Saves file locally where TF runs
}

output "marker_file_path" {
  value = local_file.pipeline_marker.filename
  description = "Path to the marker file created by Terraform."
}