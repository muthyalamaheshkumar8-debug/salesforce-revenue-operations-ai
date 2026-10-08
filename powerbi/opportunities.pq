let
 Source = Csv.Document(File.Contents(pRoot & "/data/cleaned/opportunities.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
 Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
 Typed = Table.TransformColumnTypes(Headers, {{"amount", type number}, {"probability", type number}, {"won_revenue", type number}, {"expected_revenue", type number}, {"close_date", type date}, {"created_date", type date}}, "en-US")
in Typed
