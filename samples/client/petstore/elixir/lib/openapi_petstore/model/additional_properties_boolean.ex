# NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
# https://openapi-generator.tech
# Do not edit the class manually.

defmodule OpenapiPetstore.Model.AdditionalPropertiesBoolean do
  @moduledoc """
  
  """

  @derive [Poison.Encoder]
  defstruct [
    :"name"
  ]

  @type t :: %__MODULE__{
    :"name" => String.t | nil
  }
end

defimpl Poison.Decoder, for: OpenapiPetstore.Model.AdditionalPropertiesBoolean do
  def decode(value, _options) do
    value
  end
end

