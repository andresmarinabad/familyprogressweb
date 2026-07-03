resource "vercel_project" "familyprogressweb" {
  name      = "familyprogressweb"
  
  framework = "flask"

  git_repository = {
    type = "github"
    repo = var.github_repo
  }
}

resource "vercel_deployment" "production" {
  project_id = vercel_project.familyprogressweb.id
  ref     = "main"
}

resource "vercel_project_domain" "familyprogressweb_domain" {
  project_id = vercel_project.familyprogressweb.id
  domain     = var.domain
}

resource "random_password" "secret_key" {
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

resource "random_password" "app_password" {
  length  = 16
  special = false
  upper   = true
  lower   = true
  numeric = true
}

resource "random_password" "admin_password" {
  length  = 16
  special = false
  upper   = true
  lower   = true
  numeric = true
}

resource "vercel_project_environment_variable" "secret_key" {
  project_id = vercel_project.familyprogressweb.id
  key        = "SECRET_KEY"
  value      = random_password.secret_key.result
  target     = ["production", "preview", "development"]
  sensitive  = true
}

resource "vercel_project_environment_variable" "app_password" {
  project_id = vercel_project.familyprogressweb.id
  key        = "APP_PASSWORD"
  value      = random_password.app_password.result
  target     = ["production", "preview", "development"]
  sensitive  = true
}

resource "vercel_project_environment_variable" "admin_password" {
  project_id = vercel_project.familyprogressweb.id
  key        = "ADMIN_PASSWORD"
  value      = random_password.admin_password.result
  target     = ["production", "preview", "development"]
  sensitive  = true
}

resource "vercel_project_environment_variable" "supabase_url" {
  project_id = vercel_project.familyprogressweb.id
  key        = "SUPABASE_URL"
  value      = var.supabase_url
  target     = ["production", "preview", "development"]
  sensitive  = false
}

resource "vercel_project_environment_variable" "supabase_service_role_key" {
  project_id = vercel_project.familyprogressweb.id
  key        = "SUPABASE_SERVICE_ROLE_KEY"
  value      = var.supabase_service_role_key
  target     = ["production", "preview", "development"]
  sensitive  = true
}