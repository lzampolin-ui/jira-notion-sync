JQL_QUERY = project = "GMI"
AND "client" = "US BANGLA"
AND status NOT IN (Completed, REJECTED, ROLLBACKED)
AND "show to customer" = Yes
ORDER BY "cf[10644]" ASC, created DESC
