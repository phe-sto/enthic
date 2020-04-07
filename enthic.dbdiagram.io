TABLE identity
{
  siren INT [pk, not null]
  denomination VARCHAR(100) [not null]
  ape SMALLINT [not null]
  postal_code CHAR(5) [not null]
  town VARCHAR(25) [not null]
  Indexes {
    denomination [name:'index_denomination']
  }
}
TABLE bundle
{
  siren INT [not null]
  declaration YEAR [not null]
  accountability TINYINT [not null]
  bundle TINYINT [not null]
  amount FLOAT [not null]
  Indexes {
    siren [name:'index_siren']
  }
}
Ref: "bundle"."siren" > "identity"."siren"
TABLE request
{
  method CHAR(6) [not null]
  uri VARCHAR(100) [not null]
  remote_address CHAR(15) [not null]
  remote_port INT [not null]
  agent VARCHAR(200) [not null]
  parameter VARCHAR(100)
  created TIMESTAMP [default: `now()`]
}