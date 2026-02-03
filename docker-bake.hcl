variable "RELEASE_TAG" {
    type    = string
    default = "v1.0.0"
}

target "api" {
    context    = "."
    dockerfile = "Dockerfile"
    tags = [
    "itzthedockerjules/lengauers-bistro-api:${RELEASE_TAG}",
    "itzthedockerjules/lengauers-bistro-api:latest",
  ]
    platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
}
