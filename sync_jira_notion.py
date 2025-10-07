JQL_QUERY = project = "GMI"
AND "client[dropdown]" = "US BANGLA"
AND status NOT IN (Completed, REJECTED, ROLLBACKED)
AND "show to customer[checkboxes]" = Yes
ORDER BY "cf[10644]" ASC, created DESC
