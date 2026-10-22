from flask import Flask, render_template, request, session, jsonify

app = Flask(__name__)
app.secret_key = "ask-project-secret"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/squishies")
def squishies():
    return render_template("squishies.html")


@app.route("/keychains")
def keychains():
    return render_template("keychains.html")


@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    return render_template("cart.html", cart=cart_items)


@app.route("/favourites")
def favourites():
    favourite_items = session.get("favourites", [])
    return render_template("favourites.html", favourites=favourite_items)


@app.route("/toggle_favourite", methods=["POST"])
def toggle_favourite():
    product = request.form.get("product")
    price = request.form.get("price")
    image = request.form.get("image")

    if not product or not price or not image:
        return "error", 400

    favourite_items = session.get("favourites", [])

    for item in favourite_items:
        if item["product"] == product:
            favourite_items = [
                fav for fav in favourite_items
                if fav["product"] != product
            ]
            session["favourites"] = favourite_items
            return "removed"

    favourite_items.append({
        "product": product,
        "price": price,
        "image": image
    })

    session["favourites"] = favourite_items
    return "added"


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product = request.form.get("product")
    price = request.form.get("price")
    image = request.form.get("image")

    if not product or not price or not image:
        return "error", 400

    cart_items = session.get("cart", [])

    for item in cart_items:
        if item["product"] == product:
            item["quantity"] += 1
            session["cart"] = cart_items
            return "added"

    cart_items.append({
        "product": product,
        "price": price,
        "image": image,
        "quantity": 1
    })

    session["cart"] = cart_items
    return "added"


@app.route("/toggle_cart", methods=["POST"])
def toggle_cart():
    product = request.form.get("product")
    price = request.form.get("price")
    image = request.form.get("image")
    action = request.form.get("action")

    if not product or not price or not image:
        return "error", 400

    cart_items = session.get("cart", [])

    if action == "remove":
        cart_items = [
            item for item in cart_items
            if item["product"] != product
        ]
        session["cart"] = cart_items
        return "removed"

    elif action == "add":
        for item in cart_items:
            if item["product"] == product:
                return "added"

        cart_items.append({
            "product": product,
            "price": price,
            "image": image,
            "quantity": 1
        })

        session["cart"] = cart_items
        return "added"

    return "error", 400


@app.route("/update_quantity", methods=["POST"])
def update_quantity():
    product = request.form.get("product")
    quantity = request.form.get("quantity", type=int)

    if not product or quantity is None:
        return jsonify({"error": "Missing information"}), 400

    if quantity < 1 or quantity > 99:
        return jsonify({"error": "Invalid quantity"}), 400

    cart_items = session.get("cart", [])

    for item in cart_items:
        if item["product"] == product:
            item["quantity"] = quantity
            session["cart"] = cart_items

            item_total = float(item["price"]) * quantity

            return jsonify({
                "success": True,
                "quantity": quantity,
                "item_total": round(item_total, 2)
            })

    return jsonify({"error": "Product not found"}), 404


@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    product = request.form.get("product")

    if not product:
        return jsonify({"error": "Missing product"}), 400

    cart_items = session.get("cart", [])

    cart_items = [
        item for item in cart_items
        if item["product"] != product
    ]

    session["cart"] = cart_items

    return jsonify({"success": True})


@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json(silent=True) or {}

    selected_products = data.get("products", [])
    payment_method = data.get("payment_method")

    allowed_methods = [
        "Online Banking",
        "E-wallet",
        "Cash on Delivery"
    ]

    if not isinstance(selected_products, list) or not selected_products:
        return jsonify({
            "error": "Please select at least one product."
        }), 400

    if payment_method not in allowed_methods:
        return jsonify({
            "error": "Please choose a valid payment method."
        }), 400

    cart_items = session.get("cart", [])

    selected_set = set(selected_products)

    if len(selected_set) != len(selected_products):
        return jsonify({
            "error": "Invalid product selection."
        }), 400

    available_names = {
        item["product"] for item in cart_items
    }

    if not selected_set.issubset(available_names):
        return jsonify({
            "error": "Some selected products are not in your cart."
        }), 400

    purchased_items = [
        item for item in cart_items
        if item["product"] in selected_set
    ]

    subtotal = sum(
        float(item["price"]) * int(item["quantity"])
        for item in purchased_items
    )

    shipping = 5.00
    total = subtotal + shipping

    remaining_items = [
        item for item in cart_items
        if item["product"] not in selected_set
    ]

    session["cart"] = remaining_items

    return jsonify({
        "success": True,
        "message": "Order placed successfully!",
        "items": purchased_items,
        "subtotal": round(subtotal, 2),
        "shipping": shipping,
        "total": round(total, 2),
        "payment_method": payment_method
    })

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)