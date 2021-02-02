resource "random_id" "server" {
  keepers = {
    id = "${aws_db_subnet_group.dbsubnetgp.name}"
  }

  byte_length = 8
}


resource "aws_db_parameter_group" "dbpg" {
  name = "${var.rdsmetadatadbparametergroup}"
  family      = "${var.rdsmetadatafamily}"
  parameter = ["${var.rdsmetadataparameters}"]
}

resource "aws_db_subnet_group" "dbsubnetgp" {
  name        = "${var.rdsmetadatasubnetg_name}"
  description = "Group of DB subnets"
  subnet_ids  = ["${var.rdsmetadatasubnets}"]

  tags {
    envname = "${var.env}"
    envtype = "${var.envtype}"
  }
}


resource "aws_db_instance" "dbinstance" {
  instance_class      = "${var.rdsmetadatainstance_type}"
  allocated_storage    = "${var.rdsmetadata_storage}"
  engine               = "${var.rdsmetadataengine}"
  name                 = "${var.rdsmetadataname}"
  username             = "${var.rdsmetadatausername}"
  password             = "${var.rdsmetadatapassword}"
  identifier          = "${var.rdsmetadatainstance_name}"
  db_subnet_group_name         = "${aws_db_subnet_group.dbsubnetgp.name}"
  parameter_group_name         = "${aws_db_parameter_group.dbpg.name}"
  final_snapshot_identifier    = "${var.final_snapshot_identifier}-${random_id.server.hex}"
  skip_final_snapshot          = "${var.skip_final_snapshot}"
  backup_retention_period         = "${var.rdsmetadatabackup_retention_period}"
  port                            = "${var.rdsmetadataport}"
  vpc_security_group_ids          = ["${var.rdsmetadatasecurity_groups}"]
  snapshot_identifier             = "${var.rdsmetadatasnapshot_identifier}"
}

