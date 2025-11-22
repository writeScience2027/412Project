--
-- PostgreSQL database dump
--

\restrict wr27Hr0e5KpjvA5cA5LiY54aNNgrhlwRwtA8AIUOCF2sfE6ffGUxLjX7UrPoNYF

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: book; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.book (
    numavailable integer,
    title character varying(500),
    author character varying(50),
    genre character varying(50),
    audienceage integer,
    releaseyear integer,
    totalquantity integer,
    isbn integer NOT NULL
);


ALTER TABLE public.book OWNER TO postgres;

--
-- Name: checkedout; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.checkedout (
    userid character varying(50),
    isbn integer,
    isoverdue boolean,
    returndate date,
    duedate date,
    borrowdate date
);


ALTER TABLE public.checkedout OWNER TO postgres;

--
-- Name: librarian; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.librarian (
    userid character varying(50)
);


ALTER TABLE public.librarian OWNER TO postgres;

--
-- Name: reader; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reader (
    userid character varying(50),
    numbookscheckedout integer NOT NULL
);


ALTER TABLE public.reader OWNER TO postgres;

--
-- Name: status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.status (
    userid character varying(50),
    isbn integer,
    added character varying(50),
    removed character varying(50)
);


ALTER TABLE public.status OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    userid character varying(50) NOT NULL,
    password character varying(50) NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: book; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.book (numavailable, title, author, genre, audienceage, releaseyear, totalquantity, isbn) FROM stdin;
9	Harry Potter and the Chamber of Secrets	J.K. Rowling	Fantasy	12	1998	10	100000001
7	To Kill a Mockingbird	Harper Lee	Fiction	14	1960	8	100000004
5	The Road	C. McCarthy	Fiction	16	2006	6	100000010
2	Fluent Python	L. Ramalho	Tech	18	2015	3	100000011
2	Effective Java	J. Bloch	Tech	18	2018	3	100000012
3	Clean Code	R.C. Martin	Tech	18	2008	4	100000013
6	Harry Potter and the Sorcerer's Stone	J.K. Rowling	Fantasy	12	1997	6	100000002
5	The Catcher in the Rye	J.D. Salinger	Fiction	16	1951	5	100000003
7	Fahrenheit 451	Ray Bradbury	Sci-Fi	14	1953	7	100000005
9	The Hobbit	J.R.R. Tolkien	Fantasy	10	1937	9	100000006
4	Into Thin Air	Jon Krakauer	Nonfiction	16	1997	4	100000007
3	The Odyssey	Homer	Classics	16	1999	3	100000008
5	Guns, Germs, and Steel	Jared Diamond	Nonfiction	16	1997	5	100000009
2	Design Patterns	GoF	Tech	18	1994	2	100000014
2	Designing Data-Intensive Applications	M. Kleppmann	Tech	18	2017	2	100000015
\.


--
-- Data for Name: checkedout; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.checkedout (userid, isbn, isoverdue, returndate, duedate, borrowdate) FROM stdin;
r_alex	100000001	t	\N	2025-11-21	2025-11-08
r_bailey	100000006	f	2025-11-15	2025-11-16	2025-11-02
r_cody	100000004	t	\N	2025-11-19	2025-11-05
r_dana	100000003	f	2025-11-12	2025-11-06	2025-10-23
r_alex	100000009	f	2025-10-08	2025-10-07	2025-09-23
r_bailey	100000009	f	2025-10-24	2025-10-23	2025-10-09
r_cody	100000009	f	2025-11-10	2025-11-08	2025-10-25
r_bailey	100000011	f	\N	2025-11-26	2025-11-12
r_dana	100000013	f	\N	2025-11-28	2025-11-14
r_cody	100000010	f	\N	2025-11-24	2025-11-10
r_alex	100000010	f	2025-10-28	2025-10-27	2025-10-13
r_dana	100000002	f	2025-10-23	2025-10-17	2025-10-03
r_alex	100000012	t	\N	2025-11-21	2025-11-07
\.


--
-- Data for Name: librarian; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.librarian (userid) FROM stdin;
l_morgan
l_sky
l_taylor
\.


--
-- Data for Name: reader; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reader (userid, numbookscheckedout) FROM stdin;
r_alex	2
r_bailey	1
r_cody	2
r_dana	1
\.


--
-- Data for Name: status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.status (userid, isbn, added, removed) FROM stdin;
l_morgan	100000001	2025-08-20	\N
l_morgan	100000002	2025-08-21	\N
l_sky	100000006	2025-08-22	\N
l_taylor	100000011	2025-08-23	\N
l_taylor	100000013	2025-08-24	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (userid, password) FROM stdin;
r_alex	pw_alex_1
r_bailey	pw_bailey_2
r_cody	pw_cody_3
r_dana	pw_dana_4
l_morgan	pw_morgan_5
l_sky	pw_sky_6
l_taylor	pw_taylor_7
\.


--
-- Name: book book_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.book
    ADD CONSTRAINT book_pkey PRIMARY KEY (isbn);


--
-- Name: users users_password_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_password_key UNIQUE (password);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);


--
-- Name: checkedout checkedout_isbn_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checkedout
    ADD CONSTRAINT checkedout_isbn_fkey FOREIGN KEY (isbn) REFERENCES public.book(isbn);


--
-- Name: checkedout checkedout_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checkedout
    ADD CONSTRAINT checkedout_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- Name: librarian librarian_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.librarian
    ADD CONSTRAINT librarian_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- Name: reader reader_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reader
    ADD CONSTRAINT reader_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- Name: status status_isbn_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_isbn_fkey FOREIGN KEY (isbn) REFERENCES public.book(isbn);


--
-- Name: status status_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- PostgreSQL database dump complete
--

\unrestrict wr27Hr0e5KpjvA5cA5LiY54aNNgrhlwRwtA8AIUOCF2sfE6ffGUxLjX7UrPoNYF

