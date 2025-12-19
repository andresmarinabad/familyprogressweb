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

resource "random_password" "api_key" {
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric  = true
}

resource "vercel_project_environment_variable" "api_key" {
  project_id = vercel_project.familyprogressweb.id
  key        = "CRON_SECRET"
  value      = random_password.api_key.result
  target     = ["production"]
}

resource "vercel_project_environment_variable" "resend_api" {
  project_id = vercel_project.familyprogressweb.id
  key        = "RESEND_KEY"
  value      = var.resend_apikey
  target     = ["production"]
}

resource "vercel_project_environment_variable" "email_to_list" {
  project_id = vercel_project.familyprogressweb.id
  key        = "EMAIL_TO"
  value      = var.email_to_list
  target     = ["production"]
}

resource "vercel_project_environment_variable" "onesignal_appid" {
  project_id = vercel_project.familyprogressweb.id
  key        = "ONESIGNAL_APPID"
  value      = var.onesignal_appid
  target     = ["production"]
}

resource "vercel_project_environment_variable" "onesignal_apikey" {
  project_id = vercel_project.familyprogressweb.id
  key        = "ONESIGNAL_APIKEY"
  value      = var.onesignal_apikey
  target     = ["production"]
}

resource "vercel_project_crons" "crons" {
  project_id = vercel_project.familyprogressweb.id
  enabled    = true
}