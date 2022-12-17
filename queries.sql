-- Index page
SELECT 
    "book"."year","book"."author_id",
    "book"."created_at","book"."category_id",
    "book"."image_url","book"."pages",
    "book"."publisher_id","book"."views",
    "book"."description","book"."title","book"."isbn"
FROM "book" 
LEFT OUTER JOIN "category" "book__category" ON "book__category"."id"="book"."category_id"
WHERE 
-- case insensetive search
    (UPPER(CAST("book"."title" AS VARCHAR)) LIKE UPPER('%american%') ESCAPE '\' 
    OR UPPER(CAST("book"."title" AS VARCHAR)) LIKE UPPER('%school%') ESCAPE '\') 
AND "book__category"."name"='Classics'
ORDER BY "book"."created_at"
DESC LIMIT 16 -- 16 books per page

-- Aggregate count
SELECT COUNT(*) FROM "book" LEFT OUTER JOIN "category" "book__category" ON "book__category"."id"="book"."category_id" WHERE (UPPER(CAST("book"."title" AS VARCHAR)) LIKE UPPER('%american%') ESCAPE '\' OR UPPER(CAST("book"."title" AS VARCHAR)) LIKE UPPER('%school%') ESCAPE '\') AND "book__category"."name"='Classics'

-- Migration example
ALTER TABLE "comment" ADD banned boolean DEFAULT false;

-- Admins view
CREATE VIEW Admins AS SELECT "user"."name", "user"."surname" FROM "user" WHERE admin is true;


-- Subqueries for intersting books
SELECT 
	"year","image_url","pages","author_id","created_at",
	"description","category_id","publisher_id","isbn","views","title"
FROM "book" WHERE "category_id" IN (
	SELECT "book"."category_id" "0"
	FROM "book"
	LEFT OUTER JOIN "user_book" ON "book"."isbn"="user_book"."book_id"
	WHERE "user_book"."user_id"='025d62af-e510-47f6-a9ef-6e9078917f9e'
);
