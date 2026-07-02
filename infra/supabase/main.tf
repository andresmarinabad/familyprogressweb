resource "random_password" "db_password" {
  length  = 32
  special = false
  upper   = true
  lower   = true
  numeric = true
}

resource "supabase_project" "familyprogressweb" {
  name              = "familyprogressweb"
  organization_id   = var.supabase_org_id
  database_password = random_password.db_password.result
  region            = "eu-central-1"
}

data "supabase_apikeys" "familyprogressweb" {
  project_ref = supabase_project.familyprogressweb.id
}

resource "null_resource" "images_bucket" {
  depends_on = [supabase_project.familyprogressweb]

  provisioner "local-exec" {
    command = <<-EOT
      curl -sf -X POST \
        "https://${supabase_project.familyprogressweb.id}.supabase.co/storage/v1/bucket" \
        -H "Authorization: Bearer ${data.supabase_apikeys.familyprogressweb.service_role_key}" \
        -H "Content-Type: application/json" \
        -d '{"id":"images","name":"images","public":true}'
    EOT
  }
}
