{
  "collection":
    (
      .collection
    ),
  "filter":
    (
      [
	.query.fields
	|to_entries[]
	|select(.value.type=="column")
	|{"key": .key, "value": ".\(.value.column)"}
      ]
      |map("\"\(.key)\": \(.value)")
      |join(", ")
    )
}
|".\(.collection)[]|{\(.filter)}"
