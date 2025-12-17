variable "vercel_api_token" {
  type      = string
  sensitive = true
}

variable "github_repo" {
  type    = string
  default = "andresmarinabad/familyprogressweb"
}

variable "domain" {
  type = string
}