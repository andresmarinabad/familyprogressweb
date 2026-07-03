output "project_url" {
  value = "https://vercel.com/${vercel_project.familyprogressweb.name}"
}

output "app_password" {
  value     = random_password.app_password.result
  sensitive = true
}

output "admin_password" {
  value     = random_password.admin_password.result
  sensitive = true
}