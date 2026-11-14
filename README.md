<h1 align="center">EcoFinds</h1>

<p align="center">
  A second-hand marketplace for pre-loved items, built with Flask.<br />
  Sign in with Google, list what you no longer need, and buyers can add it to a cart or buy it now.
</p>

<p align="center">
  <a href="https://eco-finds-mu.vercel.app/">Live demo</a>
  ·
  <a href="#running-it-locally">Run it locally</a>
</p>

EcoFinds is a marketplace for second-hand items. Sellers post a listing with a title, description, whole-rupee price and an optional image URL. Buyers search, filter by category, price or status, and add items to a cart or wishlist. Guests can fill a cart before they sign in, and the cart moves to their account when they do.

It is a Flask app that renders Jinja templates on the server, with SQLAlchemy models and Bootstrap 5 for the layout. Sign-in needs a Google OAuth client. Data lives in MySQL by default, or in PostgreSQL through `DATABASE_URL`.

## What you get

- **Google sign-in, no passwords.** Sign-in runs the OpenID Connect flow against Google with the `openid email profile` scopes. The app keys each user on Google's `sub` value and creates the account the first time you sign in.
- **Guest carts that carry over.** A guest cart is tied to a session cookie. When you sign in, items move to your account, duplicates are dropped, and sold items are discarded.
- **Sold items leave every cart.** The first purchase sets the listing's buyer. That purchase removes the listing from every cart and wishlist, and its page shows Sold.
- **Search and filters.** Search matches titles and descriptions regardless of case. Filters narrow the catalog by category, minimum and maximum price, and whether an item is available or sold.
- **Buy now and checkout.** Buy now buys one listing. Checkout buys every item still available in your cart, and tells you about any that sold in the meantime.
- **Owner-only changes.** Only the seller can edit or delete a listing. Only a review's author can delete that review.
- **Reviews and wishlist.** Signed-in users rate a listing from one to five stars with a comment. The wishlist keeps sold items so you can see what happened to them, and it moves an available item into your cart in one step.
- **Orders and earnings.** My Orders lists what you bought, with a review form for each purchase. My Listings shows how many items you are selling and totals the prices of your sold listings as earnings.

## Running it locally

You need Python 3, a MySQL or PostgreSQL database, and a Google OAuth client for sign-in.

### Install dependencies

```sh
git clone https://github.com/Anuraj-dev/EcoFinds.git
cd EcoFinds
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

```sh
cp .env.example .env
```

Fill in `.env`:

| Variable | What it does |
| --- | --- |
| `SECRET_KEY` | Signs the session cookie. If it is unset, the app uses a fixed built-in key, so set your own. |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID. |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret. |
| `DATABASE_URL` | A full database URL. When it is set, it replaces the `DB_` variables. `postgres://` and `postgresql://` are rewritten for the psycopg2 driver. |
| `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | MySQL connection, used when `DATABASE_URL` is empty. Defaults are `localhost`, `root`, no password and `ecofinds`. On localhost, the app tries to create the database if it is missing. |

### Set up Google sign-in

1. In the Google Cloud Console, create an OAuth client ID for a web application.
2. Add `http://localhost:5000/auth/google/callback` as an authorized redirect URI.
3. Copy the client ID and secret into `.env`.

A deployed copy needs the same `/auth/google/callback` path on its own domain. The app builds the callback URL from the host it is served on.

### Start the app

```sh
python app.py
```

Open `http://localhost:5000`. The app creates its tables on the first request, so there is no migration step.

To load sample data, run `python models/initData.py`. It adds 20 sample listings under a seller called EcoFinds Store.

To start over, run `python reset_db.py`. It drops every table and recreates it, so all data is lost.

### Deploy on Vercel

`vercel.json` sends every request to `api/index.py`, which exposes the Flask app to Vercel's Python runtime. Set the same environment variables in the Vercel project, and point `DATABASE_URL` at a hosted database, because the serverless function cannot reach your local database.

## Does it take payments?

No. Buy now and checkout record the sale and show the item under My Orders. No card is charged, and no payment provider is connected.

## Where things live

| Path | Contents |
| --- | --- |
| `app.py` | Every route: listings, cart, checkout, wishlist, reviews, and Google sign-in. |
| `models/` | SQLAlchemy models: `User`, `Product`, `Review`, `CartItem` and `Wishlist`. |
| `auth.py`, `config.py`, `database.py` | Login manager, environment settings and database URL handling. |
| `templates/` | Jinja pages. `layouts/` holds the shared layout, navbar and footer. |
| `static/` | One stylesheet per page area, and `js/product-interactions.js` for add-to-cart and the cart badge. |
| `reset_db.py`, `models/initData.py` | Drop and recreate the schema, and load sample listings. |

## Known limitations

- Listings take an image URL only. There is no file upload, and a listing without one shows a default photo.
- Forms do not carry CSRF tokens.
- The repo has no tests.
- The schema comes from `db.create_all()`, and there are no migrations. Changing a model means a manual migration or running `reset_db.py`, which deletes data.

## License

MIT. See [LICENSE](LICENSE).
