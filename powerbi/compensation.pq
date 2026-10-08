let
 Source = Csv.Document(File.Contents(pRoot & "/data/cleaned/compensation.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
 Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
 Typed = Table.TransformColumnTypes(Headers, {{"target", type number}, {"actual", type number}, {"achievement", type number}, {"commission_rate", type number}, {"payout", type number}, {"won_deals", Int64.Type}, {"closed_deals", Int64.Type}, {"win_rate", type number}}, "en-US")
in Typed
