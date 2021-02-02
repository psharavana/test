variable "rdsmetadatasubnetg_name" {
  type        = "string"
  description = "Name given to DB subnet group"
}

variable "rdsmetadatasubnets" {
  type        = "list"
  description = "List of subnet IDs to use"
}

variable "env" {
  type        = "string"
  description = "Environment name (eg,test, stage or prod)"
}

variable "envtype" {
  type        = "string"
  description = "Environment type (eg,prod or nonprod)"
}

variable "rdsmetadataengine" {
  type        = "string"
  default     = "mysql"
  description = "mysql"
}

variable "rdsmetadatainstance_type" {
   type        = "string"
   description = "Instance type (eg db.r4.large)"
}
variable "rdsmetadata_storage" {
   type        = "string"
   description = "Instance type (eg db.r4.large)"
}
variable "rdsmetadatainstance_name" {
   type        = "string"
   description = "Instance name to be created (eg uatatlasmetadata)"
}
variable "rdsmetadataparameters" {
  description = "A list of DB parameter maps to apply"
  default     = []
}
variable "rdsmetadatadbparametergroup" {
   type        = "string"
   description = "Database ParameterGroup Name"
}
variable "rdsmetadatafamily" {
  description = "The family of the DB parameter group"
}
variable "final_snapshot_identifier" {
  type        = "string"
  default     = "final"
  description = "The name to use when creating a final snapshot on cluster destroy, appends a random 8 digits to name to ensure it's unique too."
}
variable "skip_final_snapshot" {
  type        = "string"
  default     = "false"
  description = "Should a final snapshot be created on cluster destroy"
}
variable "rdsmetadatasecurity_groups" {
  type        = "list"
  description = "VPC Security Group IDs"
}
variable "rdsmetadatasnapshot_identifier" {
  type        = "string"
  default     = ""
  description = "DB snapshot to create this database from"
}

variable "rdsmetadatabackup_retention_period" {
  type        = "string"
  default     = "7"
  description = "How long to keep backups for (in days)"
}

variable "rdsmetadatapreferred_backup_window" {
  type        = "string"
  default     = "02:00-03:00"
  description = "When to perform DB backups"
}

variable "rdsmetadatapreferred_maintenance_window" {
  type        = "string"
  default     = "sun:05:00-sun:06:00"
  description = "When to perform DB maintenance"
}

variable "rdsmetadataport" {
  type        = "string"
  default     = "3306"
  description = "The port on which to accept connections"
}

variable "rdsmetadataname" {
  type        = "string"
  description = "Name given to DB"
}

variable "rdsmetadatausername" {
  default     = "root"
  description = "Master DB username"
}

variable "rdsmetadatapassword" {
  type        = "string"
  description = "Master DB password"
}

