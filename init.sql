
CREATE TABLE IF NOT EXISTS public.author
(
    id integer NOT NULL DEFAULT nextval('author_id_seq'::regclass),
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    surname character varying(255) COLLATE pg_catalog."default" NOT NULL,
    bio character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT author_pkey PRIMARY KEY (id)
)


CREATE TABLE IF NOT EXISTS public.book
(
    isbn character varying(255) COLLATE pg_catalog."default" NOT NULL,
    title character varying(255) COLLATE pg_catalog."default" NOT NULL,
    description character varying(512) COLLATE pg_catalog."default" NOT NULL,
    image_url character varying(255) COLLATE pg_catalog."default" NOT NULL,
    year integer NOT NULL,
    pages integer NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    views integer NOT NULL,
    author_id integer NOT NULL,
    category_id integer NOT NULL,
    publisher_id integer NOT NULL,
    CONSTRAINT book_pkey PRIMARY KEY (isbn),
    CONSTRAINT book_author_id_fkey FOREIGN KEY (author_id)
        REFERENCES public.author (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT book_category_id_fkey FOREIGN KEY (category_id)
        REFERENCES public.category (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT book_publisher_id_fkey FOREIGN KEY (publisher_id)
        REFERENCES public.publisher (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)


CREATE TABLE IF NOT EXISTS public.category
(
    id integer NOT NULL DEFAULT nextval('category_id_seq'::regclass),
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT category_pkey PRIMARY KEY (id)
)


CREATE TABLE IF NOT EXISTS public.downloadsource
(
    id integer NOT NULL DEFAULT nextval('downloadsource_id_seq'::regclass),
    filetype character varying(10) COLLATE pg_catalog."default" NOT NULL,
    url character varying(128) COLLATE pg_catalog."default" NOT NULL,
    book_id character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT downloadsource_pkey PRIMARY KEY (id),
    CONSTRAINT downloadsource_book_id_fkey FOREIGN KEY (book_id)
        REFERENCES public.book (isbn) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

CREATE TABLE IF NOT EXISTS public.feedback
(
    id integer NOT NULL DEFAULT nextval('feedback_id_seq'::regclass),
    title character varying(255) COLLATE pg_catalog."default" NOT NULL,
    email character varying(255) COLLATE pg_catalog."default" NOT NULL,
    issue_type integer NOT NULL,
    message character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT feedback_pkey PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS public.notification
(
    id integer NOT NULL DEFAULT nextval('notification_id_seq'::regclass),
    message character varying(255) COLLATE pg_catalog."default" NOT NULL,
    user_id uuid NOT NULL,
    CONSTRAINT notification_pkey PRIMARY KEY (id),
    CONSTRAINT notification_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

CREATE TABLE IF NOT EXISTS public.publisher
(
    id integer NOT NULL DEFAULT nextval('publisher_id_seq'::regclass),
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT publisher_pkey PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS public."user"
(
    id uuid NOT NULL,
    admin boolean NOT NULL,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    surname character varying(255) COLLATE pg_catalog."default" NOT NULL,
    bio character varying(255) COLLATE pg_catalog."default" NOT NULL,
    email character varying(255) COLLATE pg_catalog."default" NOT NULL,
    password_hash character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (id)
)
