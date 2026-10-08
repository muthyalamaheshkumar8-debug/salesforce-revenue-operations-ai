let
 Source = Csv.Document(File.Contents(pRoot & "/data/cleaned/sales_reps.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
 Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
 Typed = Table.TransformColumnTypes(Headers, {{"target", type number}, {"commission_rate", type number}}, "en-US")
in Typed
