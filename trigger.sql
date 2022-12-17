CREATE TRIGGER notify_admin
	AFTER INSERT
	ON "comment"
	FOR EACH ROW
	EXECUTE PROCEDURE send_notification();
