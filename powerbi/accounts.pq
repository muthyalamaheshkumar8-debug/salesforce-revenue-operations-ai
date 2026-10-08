let
 Source = Csv.Document(File.Contents(pRoot & "/data/cleaned/accounts.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
 Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
 Typed = Table.TransformColumnTypes(Headers, {}, "en-US")
in Typed
