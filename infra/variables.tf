variable "vercel_api_token" {
  type      = string
  sensitive = true
}

variable "github_repo" {
  type    = string
}

variable "domain" {
  type = string
}

variable "resend_apikey" {
  type = string
  sensitive = true
}

variable "email_to_list" {
  type = string
}