CREATE FUNCTION send_notification()
	RETURNS TRIGGER
	LANGUAGE PLPGSQL
	AS
$$
BEGIN
	INSERT INTO "notification"(message, user_id)
	VALUES (NEW.message, '025d62af-e510-47f6-a9ef-6e9078917f9e');
	RETURN NEW;
END;
$$
