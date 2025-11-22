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
    """Inject rows after the header row of the specified table."""
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
    """Generate table rows matching frontend column structure."""
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
            tr = (
                f"<tr>"
                f"<td>{title}</td><td>{author}</td><td>{isbn}</td><td>{genre}</td>"
                f"<td>{audience}</td><td>{year}</td><td>{numavailable}</td><td>{totalq}</td>"
                f"</tr>"
            )
        else:
            tr = (
                f"<tr>"
                f"<td><input type='checkbox' name='selected_isbn' value='{isbn}'></td>"
                f"<td>{title}</td><td>{author}</td><td>{isbn}</td><td>{genre}</td>"
                f"<td>{audience}</td><td>{year}</td><td>{numavailable}</td><td>{totalq}</td>"
                f"</tr>"
            )
        out.append(tr)
    return "\n".join(out)

def render_loans_rows(loan_rows):
    """Generate table rows matching reader_profile.html structure (7 columns)."""
    out = []
    for l in loan_rows:
        isbn = l.get("isbn")
        title = l.get("title") or ""
        author = l.get("author") or ""
        borrowdate = l.get("borrowdate") or l.get("borrowDate") or ""
        duedate = l.get("duedate") or l.get("dueDate") or ""
        isoverdue = l.get("isoverdue") or l.get("isOverdue") or False
        overdue_str = "Yes" if isoverdue else "No"
        returndate = l.get("returndate") or l.get("returnDate") or "N/A"
        
        tr = (
            f"<tr>"
            f"<td>{title}</td><td>{author}</td><td>{isbn}</td>"
            f"<td>{borrowdate}</td><td>{duedate}</td>"
            f"<td>{overdue_str}</td><td>{returndate}</td>"
            f"</tr>"
        )
        out.append(tr)
    return "\n".join(out)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userid = request.form.get("userid")
        password = request.form.get("password")
        
        if not userid or not password:
            flash("Please enter both UserID and Password", "warning")
            return redirect(url_for("login"))
        
        conn = get_db_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute("SELECT userID, password FROM users WHERE userID = %s", (userid,))
            user = cur.fetchone()
            
            if user and user['password'] == password:
                session['userID'] = userid
                
                cur.execute("SELECT 1 FROM librarian WHERE userID = %s", (userid,))
                if cur.fetchone():
                    session['role'] = 'librarian'
                    flash(f"Welcome, {userid}!", "success")
                    return redirect(url_for('cataloglibrarian'))
                else:
                    session['role'] = 'reader'
                    flash(f"Welcome, {userid}!", "success")
                    return redirect(url_for('catalog'))
            else:
                flash("Invalid UserID or Password", "danger")
                return redirect(url_for("login"))
        finally:
            cur.close()
            conn.close()
    
    return send_from_directory(STATIC_HTML_DIR, 'index.html')

@app.route("/setuser/<userid>")
def set_user(userid):
    """Quick demo helper to set session user (no password)."""
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
    return redirect(url_for('login'))

@app.route("/catalog")
def catalog():
    """Reader catalog page with search functionality."""
    q = request.args.get("q", "").strip()

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
    """Librarian catalog page with search functionality."""
    if session.get('role') != 'librarian':
        flash("You must be a librarian to access this page.", "warning")
        return redirect(url_for('catalog'))

    q = request.args.get("q", "").strip()
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

    rows_html = render_catalog_rows(books, reader_mode=False)
    base_html = read_static_html("cataloglibrarian.html")
    new_html = inject_rows_into_table(base_html, rows_html, table_index=0)
    return Response(new_html, mimetype="text/html")


@app.route("/reader_profile")
def reader_profile():
    """Reader profile page showing checked out books."""
    user = session.get("userID")
    if not user:
        flash("Not logged in. Use /setuser/<id> for demo login.", "warning")
        return redirect(url_for('catalog'))

    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT r.numBooksCheckedOut, u.userID
            FROM reader r
            JOIN users u ON r.userID = u.userID
            WHERE r.userID = %s
        """, (user,))
        user_info = cur.fetchone()
        
        cur.execute("""
            SELECT b.isbn, b.title, b.author, ch.borrowDate AS borrowdate, 
                   ch.dueDate AS duedate, ch.returnDate, ch.isOverdue
            FROM checkedOut ch
            JOIN book b ON ch.isbn = b.isbn
            WHERE ch.userID = %s
            ORDER BY ch.borrowDate DESC
        """, (user,))
        loans = cur.fetchall()
    finally:
        cur.close(); conn.close()

    base_html = read_static_html("reader_profile.html")
    if user_info:
        base_html = base_html.replace("ex: userId", user_info['userid'])
        base_html = base_html.replace("ex: 5", str(user_info['numbookscheckedout']))
    
    rows_html = render_loans_rows(loans)
    new_html = inject_rows_into_table(base_html, rows_html, table_index=0)
    return Response(new_html, mimetype="text/html")


@app.route("/librarian_profile")
def librarian_profile():
    """Librarian profile page."""
    if session.get('role') != 'librarian':
        flash("Must be a librarian", "warning")
        return redirect(url_for('catalog'))
    
    user = session.get("userID")
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT b.isbn, b.title, b.author, 
                   CURRENT_DATE AS borrowdate, 
                   CURRENT_DATE AS duedate,
                   FALSE AS isoverdue,
                   NULL AS returndate
            FROM book b
            LIMIT 10
        """)
        books = cur.fetchall()
    finally:
        cur.close(); conn.close()
    
    base_html = read_static_html("librarian_profile.html")
    base_html = base_html.replace("ex: userId", user)
    
    rows_html = render_loans_rows(books)
    new_html = inject_rows_into_table(base_html, rows_html, table_index=0)
    return Response(new_html, mimetype="text/html")


@app.route("/librarian_view")
def librarian_view():
    """Librarian book catalog management page."""
    if session.get('role') != 'librarian':
        flash("Must be a librarian", "warning")
        return redirect(url_for('catalog'))
    
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT isbn, title, author, genre, audienceage, releaseyear, numavailable, totalquantity
            FROM book
            ORDER BY title
        """)
        books = cur.fetchall()
    finally:
        cur.close(); conn.close()
    
    rows_html = render_catalog_rows(books, reader_mode=False)
    base_html = read_static_html("librarian_view.html")
    new_html = inject_rows_into_table(base_html, rows_html, table_index=0)
    return Response(new_html, mimetype="text/html")


@app.route("/users")
def users_page():
    """Users page for librarians."""
    if session.get('role') != 'librarian':
        flash("Must be a librarian", "warning")
        return redirect(url_for('catalog'))

    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("""
            SELECT u.userID, b.title, b.author, ch.isbn, 
                   ch.borrowDate AS borrowdate, ch.dueDate AS duedate, 
                   ch.returnDate, ch.isOverdue
            FROM users u
            LEFT JOIN checkedOut ch ON u.userID = ch.userID
            LEFT JOIN book b ON ch.isbn = b.isbn
            WHERE u.userID LIKE 'r_%'
            ORDER BY u.userID
        """)
        rows_data = cur.fetchall()
    finally:
        cur.close(); conn.close()

    out = []
    for r in rows_data:
        userid = r.get("userid") or r.get("userID") or ""
        title = r.get("title") or ""
        author = r.get("author") or ""
        isbn = r.get("isbn") or ""
        borrow = r.get("borrowdate") or ""
        due = r.get("duedate") or ""
        isover = r.get("isoverdue") or False
        overdue_str = "Yes" if isover else "No"
        returndate = r.get("returndate") or "N/A"
        
        tr = (f"<tr><td>{userid}</td><td>{title}</td><td>{author}</td><td>{isbn}</td>"
              f"<td>{borrow}</td><td>{due}</td><td>{overdue_str}</td><td>{returndate}</td></tr>")
        out.append(tr)
    rows_html = "\n".join(out)

    base_html = read_static_html("users.html")
    new_html = inject_rows_into_table(base_html, rows_html, table_index=0)
    return Response(new_html, mimetype="text/html")


@app.route("/cstyle.css")
def serve_cstyle():
    return send_from_directory(os.path.join(app.root_path, 'static', 'css'), 'cstyle.css')

@app.route("/style.css")
def serve_style():
    return send_from_directory(os.path.join(app.root_path, 'static', 'css'), 'style.css')

@app.route("/<path:filename>")
def serve_static_html(filename):
    if filename.endswith('.html'):
        return send_from_directory(STATIC_HTML_DIR, filename)
    return "Not found", 404


@app.route("/whoami")
def whoami():
    return {"user": session.get("userID"), "role": session.get("role")}


if __name__ == "__main__":
    print("Starting Flask app. Session secret:", app.secret_key)
    print("Serving static HTML from:", STATIC_HTML_DIR)
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
