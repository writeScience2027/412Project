from flask import Flask, request, session, redirect, url_for, flash, Response
from db import get_connection
import psycopg2.extras
import os
import re
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = "cse412_demo_secret"

STATIC_HTML_DIR = os.path.join(os.path.dirname(__file__), "templates_static")

def read_static_html(filename):
    path = os.path.join(STATIC_HTML_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

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
        numavailable = b.get("numavailable") if b.get("numavailable") is not None else b.get("numAvailable", "")
        totalq = b.get("totalquantity") if b.get("totalquantity") is not None else b.get("totalQuantity", "")
        if reader_mode:
            checkout_href = f"?checkout={isbn}"
            tr = f"<tr><td>{title}</td><td>{author}</td><td>{isbn}</td><td>{genre}</td><td>{audience}</td><td>{year}</td><td>{numavailable}</td><td>{totalq}</td><td><a href=\"{checkout_href}\">Checkout</a></td></tr>"
        else:
            remove_href = f"?remove={isbn}"
            tr = f"<tr><td><input type='checkbox' name='selected_isbn' value='{isbn}'></td><td>{title}</td><td>{author}</td><td>{isbn}</td><td>{genre}</td><td>{audience}</td><td>{year}</td><td>{numavailable}</td><td>{totalq}</td><td><a href=\"{remove_href}\">Remove</a></td></tr>"
        out.append(tr)
    return "\n".join(out)

@app.route("/setuser/<userid>")
def set_user(userid):
    """Quick helper to set session user for demo (no password)."""
    session['userID'] = userid
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM librarian WHERE userid = %s", (userid,))
    if cur.fetchone():
        session['role'] = 'librarian'
    else:
        session['role'] = 'reader'
    flash(f"Session set as {userid} ({session.get('role')})", "info")
    if session['role'] == 'librarian':
        return redirect(url_for('cataloglibrarian'))
    return redirect(url_for('catalog'))

@app.route("/catalog")
def catalog():
    user = session.get('userID')

    checkout_isbn = request.args.get("checkout")
    if checkout_isbn and user:
        conn = get_connection()
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
        base_html = read_static_html("catalog.html")
        return redirect(url_for('catalog'))

    q = request.args.get("q", "").strip()
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
    rows_html = render_catalog_rows(books, reader_mode=True)

    base_html = read_static_html("catalog.html")
    new_html = inject_rows_into_table(base_html, rows_html, table_index=0)
    return Response(new_html, mimetype="text/html")


@app.route("/cataloglibrarian")
def cataloglibrarian():
    if session.get('role') != 'librarian':
        flash("Not a librarian", "warning")
        return redirect(url_for('catalog'))

    remove_isbn = request.args.get("remove")
    if remove_isbn:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM status WHERE isbn = %s", (remove_isbn,))
            cur.execute("DELETE FROM book WHERE isbn = %s", (remove_isbn,))
            conn.commit()
            flash("Removed book " + str(remove_isbn), "success")
        except Exception as e:
            conn.rollback()
            flash("Remove failed: " + str(e), "danger")
        return redirect(url_for('cataloglibrarian'))

    q = request.args.get("q", "").strip()
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
    rows_html = render_catalog_rows(books, reader_mode=False)
    base_html = read_static_html("cataloglibrarian.html")
    new_html = inject_rows_into_table(base_html, rows_html, table_index=0)
    return Response(new_html, mimetype="text/html")


@app.route("/return")
def return_book():
    isbn = request.args.get("isbn")
    user = session.get('userID')
    if not user or not isbn:
        flash("Missing user or isbn", "warning")
        return redirect(url_for('catalog'))
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE checkedOut
            SET returnDate = CURRENT_DATE, isOverdue = FALSE
            WHERE userID = %s AND isbn = %s AND returnDate IS NULL
        """, (user, isbn))
        cur.execute("UPDATE book SET numavailable = numavailable + 1 WHERE isbn = %s", (isbn,))
        cur.execute("UPDATE reader SET numBooksCheckedOut = GREATEST(numBooksCheckedOut - 1, 0) WHERE userID = %s", (user,))
        conn.commit()
        flash("Returned " + str(isbn), "success")
    except Exception as e:
        conn.rollback()
        flash("Return failed: " + str(e), "danger")
    return redirect(url_for('catalog'))

@app.route("/set-css")
def set_css_redirect():
    return redirect(url_for('static', filename='css/cstyle.css'))

@app.route("/whoami")
def whoami():
    return {"user": session.get("userID"), "role": session.get("role")}

if __name__ == "__main__":
    app.run(debug=True)
