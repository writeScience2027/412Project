import os
import re
from urllib.parse import urlencode

from flask import (
    Flask, request, redirect, url_for, session, flash, Response, send_from_directory
)
import psycopg2.extras

try:
    from db import get_connection as get_db_conn
except Exception:
    try:
        from db import get_db as get_db_conn
    except Exception:
        get_db_conn = None

if get_db_conn is None:
    raise RuntimeError(
        "db.py not found or does not define get_connection/get_db. "
        "Create db.py with a function get_connection()/get_db() that returns a psycopg2 connection."
    )

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "cse412_demo_secret")

STATIC_HTML_DIR = os.path.join(os.path.dirname(__file__), "templates_static")


def read_static_html(filename):
    path = os.path.join(STATIC_HTML_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Static HTML file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()

def inject_rows_into_table(html, rows_html, table_index=0):
    table_pattern = re.compile(r"(<table.*?>)(.*?)(</table>)", re.IGNORECASE | re.DOTALL)
    matches = list(table_pattern.finditer(html))
    if not matches or table_index >= len(matches):
        return html.replace("</table>", rows_html + "</table>", 1)
    m = matches[table_index]
    table_html = m.group(0)
    header_end = re.search(r"</tr>", table_html, re.IGNORECASE)
    if not header_end:
        new_table = table_html.replace("</table>", rows_html + "</table>", 1)
    else:
        idx = header_end.end()
        new_table = table_html[:idx] + rows_html + table_html[idx:]
    new_html = html[:m.start()] + new_table + html[m.end():]
    return new_html

def render_catalog_rows(book_rows, reader_mode=True):
    out = []
    for b in book_rows:
        isbn = b.get("isbn")
        title = b.get("title") or ""
        author = b.get("author") or ""
        genre = b.get("genre") or ""
        audience = b.get("audienceage") or b.get("audienceAge") or ""
        year = b.get("releaseyear") or b.get("releaseYear") or ""
        numavailable = b.get("numavailable")
        if numavailable is None:
            numavailable = b.get("numAvailable", "")
        totalq = b.get("totalquantity") if b.get("totalquantity") is not None else b.get("totalQuantity", "")
        if reader_mode:
            checkout_href = f"{url_for('catalog')}?checkout={isbn}"
            tr = (
                f"<tr>"
                f"<td>{title}</td><td>{author}</td><td>{isbn}</td><td>{genre}</td>"
                f"<td>{audience}</td><td>{year}</td><td>{numavailable}</td><td>{totalq}</td>"
                f"<td><a href=\"{checkout_href}\">Checkout</a></td>"
                f"</tr>"
            )
        else:
            remove_href = f"{url_for('cataloglibrarian')}?remove={isbn}"
            tr = (
                f"<tr>"
                f"<td><input type='checkbox' name='selected_isbn' value='{isbn}'></td>"
                f"<td>{title}</td><td>{author}</td><td>{isbn}</td><td>{genre}</td>"
                f"<td>{audience}</td><td>{year}</td><td>{numavailable}</td><td>{totalq}</td>"
                f"<td><a href=\"{remove_href}\">Remove</a></td>"
                f"</tr>"
            )
        out.append(tr)
    return "\n".join(out)

def render_loans_rows(loan_rows):
    out = []
    for l in loan_rows:
        isbn = l.get("isbn")
        title = l.get("title") or ""
        borrowdate = l.get("borrowdate") or l.get("borrowDate") or ""
        duedate = l.get("duedate") or l.get("dueDate") or ""
        isoverdue = l.get("isoverdue") or l.get("isOverdue") or False
        overdue_str = "Yes" if isoverdue else "No"
        return_href = f"{url_for('return_book')}?isbn={isbn}"
        tr = (
            f"<tr><td>{title}</td><td>{borrowdate}</td><td>{duedate}</td>"
            f"<td>{overdue_str}</td><td><a href=\"{return_href}\">Return</a></td></tr>"
        )
        out.append(tr)
    return "\n".join(out)

@app.route("/setuser/<userid>")
def set_user(userid):
    """
    Quick demo helper to set session user (no password).
    Use: /setuser/r_alex or /setuser/l_morgan
    """
    session['userID'] = userid
    conn = get_db_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM librarian WHERE userID = %s", (userid,))
        if cur.fetchone():
            session['role'] = 'librarian'
        else:
            session['role'] = 'reader'
    finally:
        cur.close(); conn.close()
    flash(f"Session set as {userid} ({session.get('role')})", "info")
    if session['role'] == 'librarian':
        return redirect(url_for('cataloglibrarian'))
    return redirect(url_for('catalog'))

@app.route("/")
def index():
    return redirect(url_for('catalog'))

@app.route("/catalog")
def catalog():
    checkout_isbn = request.args.get("checkout")
    q = request.args.get("q", "").strip()

    if checkout_isbn:
        user = session.get('userID')
        if not user:
            flash("Not logged in. Use /setuser/<id> for demo login or implement login.", "warning")
            return redirect(url_for('catalog'))
        conn = get_db_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO checkedOut (userID, isbn, borrowDate, dueDate, isOverdue)
                VALUES (%s, %s, CURRENT_DATE, (CURRENT_DATE + INTERVAL '30 days')::date, FALSE)
            """, (user, checkout_isbn))
            cur.execute("UPDATE book SET numavailable = GREATEST(numavailable - 1, 0) WHERE isbn = %s", (checkout_isbn,))
            cur.execute("UPDATE reader SET numBooksCheckedOut = numBooksCheckedOut + 1 WHERE userID = %s", (user,))
            conn.commit()
            flash("Checked out book " + str(checkout_isbn), "success")
        except Exception as e:
            conn.rollback()
            flash("Checkout failed: " + str(e), "danger")
        finally:
            cur.close(); conn.close()
        base_url = url_for('catalog')
        if q:
            return redirect(f"{base_url}?q={q}")
        return redirect(base_url)

    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if q:
            wildcard = f"%{q}%"
            cur.execute("""
                SELECT isbn, title, author, genre, audienceage, releaseyear, numavailable, totalquantity
                FROM book
                WHERE LOWER(title) LIKE LOWER(%s) OR LOWER(author) LIKE LOWER(%s) OR LOWER(genre) LIKE LOWER(%s)
                ORDER BY title
            """, (wildcard, wildcard, wildcard))
        else:
            cur.execute("""
                SELECT isbn, title, author, genre, audienceage, releaseyear, numavailable, totalquantity
                FROM book
                ORDER BY title
            """)
        books = cur.fetchall()
    finally:
        cur.close(); conn.close()

    rows_html = render_catalog_rows(books, reader_mode=True)
    base_html = read_static_html("catalog.html")
    new_html = inject_rows_into_table(base_html, rows_html, table_index=0)
    return Response(new_html, mimetype="text/html")


@app.route("/cataloglibrarian")
def cataloglibrarian():
    if session.get('role') != 'librarian':
        flash("You must be a librarian to access this page. Use /setuser/<id> to set a librarian session.", "warning")
        return redirect(url_for('catalog'))

    remove_isbn = request.args.get("remove")
    if remove_isbn:
        conn = get_db_conn(); cur = conn.cursor()
        try:
            cur.execute("DELETE FROM status WHERE isbn = %s", (remove_isbn,))
            cur.execute("DELETE FROM book WHERE isbn = %s", (remove_isbn,))
            conn.commit()
            flash(f"Removed book {remove_isbn}", "success")
        except Exception as e:
            conn.rollback()
            flash("Remove failed: " + str(e), "danger")
        finally:
            cur.close(); conn.close()
        return redirect(url_for('cataloglibrarian'))

    q = request.args.get("q", "").strip()
    conn = get_db_conn(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if q:
            wildcard = f"%{q}%"
            cur.execute("""
                SELECT isbn, title, author, genre, audienceage, releaseyear, numavailable, totalquantity
                FROM book
                WHERE LOWER(title) LIKE LOWER(%s) OR LOWER(author) LIKE LOWER(%s) OR LOWER(genre) LIKE LOWER(%s)
                ORDER BY title
            """, (wildcard, wildcard, wildcard))
        else:
            cur.execute("""
                SELECT isbn, title, author, genre, audienceage, releaseyear, numavailable, totalquantity
                FROM book
                ORDER BY title
            """)
        books = cur.fetchall()
    finally:
        cur.close(); conn.close()

    rows_html = render_catalog_rows(books, reader_mode=False)
    base_html = read_static_html("cataloglibrarian.html")
    new_html = inject_rows_into_table(base_html, rows_html, table_index=0)
    return Response(new_html, mimetype="text/html")


@app.route("/return")
def return_book():
    isbn = request.args.get("isbn")
    user = session.get("userID")
    if not user or not isbn:
        flash("Missing user or isbn for return", "warning")
        return redirect(url_for('catalog'))

    conn = get_db_conn(); cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE checkedOut
            SET returnDate = CURRENT_DATE, isOverdue = FALSE
            WHERE userID = %s AND isbn = %s AND returnDate IS NULL
        """, (user, isbn))
        cur.execute("UPDATE book SET numavailable = numavailable + 1 WHERE isbn = %s", (isbn,))
        cur.execute("UPDATE reader SET numBooksCheckedOut = GREATEST(numBooksCheckedOut - 1, 0) WHERE userID = %s", (user,))
        conn.commit()
        flash("Returned book " + str(isbn), "success")
    except Exception as e:
        conn.rollback()
        flash("Return failed: " + str(e), "danger")
    finally:
        cur.close(); conn.close()

    return redirect(url_for('catalog'))


@app.route("/profile")
def profile():
    user = session.get("userID")
    if not user:
        flash("Not logged in. Use /setuser/<id> for demo login.", "warning")
        return redirect(url_for('catalog'))

    conn = get_db_conn(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT b.isbn, b.title, ch.borrowDate AS borrowdate, ch.dueDate AS duedate, ch.returnDate, ch.isOverdue
            FROM checkedOut ch
            JOIN book b ON ch.isbn = b.isbn
            WHERE ch.userID = %s
            ORDER BY ch.borrowDate DESC
        """, (user,))
        loans = cur.fetchall()
    finally:
        cur.close(); conn.close()

    rows_html = render_loans_rows(loans)
    base_html = read_static_html("reader_profile.html")
    new_html = inject_rows_into_table(base_html, rows_html, table_index=1) 
    return Response(new_html, mimetype="text/html")


@app.route("/users")
def users_page():
    if session.get('role') != 'librarian':
        flash("Must be a librarian", "warning")
        return redirect(url_for('catalog'))

    conn = get_db_conn(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT u.userID, b.title, ch.isbn, ch.borrowDate AS borrowdate, ch.dueDate AS duedate, ch.returnDate, ch.isOverdue
            FROM users u
            LEFT JOIN checkedOut ch ON u.userID = ch.userID
            LEFT JOIN book b ON ch.isbn = b.isbn
            ORDER BY u.userID
        """)
        rows = cur.fetchall()
    finally:
        cur.close(); conn.close()

    out = []
    for r in rows:
        userid = r.get("userid") or r.get("userID")
        title = r.get("title") or ""
        isbn = r.get("isbn") or ""
        borrow = r.get("borrowdate") or ""
        due = r.get("duedate") or ""
        isover = r.get("isoverdue") or False
        overdue_str = "Yes" if isover else "No"
        tr = f"<tr><td>{userid}</td><td>{title}</td><td>{isbn}</td><td>{borrow}</td><td>{due}</td><td>{overdue_str}</td><td>{r.get('returndate') or ''}</td></tr>"
        out.append(tr)
    rows_html = "\n".join(out)

    base_html = read_static_html("users.html")
    new_html = inject_rows_into_table(base_html, rows_html, table_index=0)
    return Response(new_html, mimetype="text/html")


@app.route("/cstyle.css")
def cstyle_redirect():
    return redirect(url_for('static', filename='css/cstyle.css'))

@app.route("/style.css")
def style_redirect():
    return redirect(url_for('static', filename='css/style.css'))


@app.route("/whoami")
def whoami():
    return {"user": session.get("userID"), "role": session.get("role")}


if __name__ == "__main__":
    print("Starting Flask app. Session secret:", app.secret_key)
    print("Serving static HTML from:", STATIC_HTML_DIR)
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
