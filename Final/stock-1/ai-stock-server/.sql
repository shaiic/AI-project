SQL_SELECT_TRENDING_UP = select code, name, probability * 100 as probability, close, trade_date, trending from prediction where trade_date = ? and trending = 1 order by probability limit 10
SQL_SELECT_TRENDING_DOWN = select code, name, probability * 100 as probability, close, trade_date, trending from prediction where trade_date = ? and trending = 0 order by probability limit 10
SQL_COUNT_PREDICTION = select count(1) from prediction
SQL_SELECT_STOCK_TRENDING = select code, name, probability * 100 as probability, close, trade_date, trending from prediction where code = ? and trade_date = ?
SQL_INSERT_PREDICTION = insert into prediction(code, name, probability, close, trade_date, trending) values(?, ?, ?, ?, ?, ?)
SQL_DELETE_PREDICTION = delete from prediction where code = ? and trade_date = ?