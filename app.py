from flask import Flask, render_template, request, render_template_string
import math
from scipy.stats import binom, poisson, norm, expon, uniform, geom
import re

app = Flask(__name__)

# **Home Page Route**
@app.route('/')
def home():
    return render_template('index.html')

# **HTML Template with Bootstrap**
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Distribution Solver</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="bg-dark text-light">
    <div class="container mt-5 text-center">
        <h1 class="mb-4">📊 Probability Distribution Solver</h1>
        
        <div class="card bg-secondary text-white p-4">
            <h2>🎯 Result</h2>
            <p class="fw-bold display-6">{{ result }}</p>
        </div>

        <div class="mt-4">
            <h3>📖 Steps</h3>
            <pre class="bg-light text-dark p-3 rounded">{{ steps }}</pre>
        </div>

        <a href="/" class="btn btn-primary mt-3">🔄 Try Another</a>
    </div>
</body>
</html>
"""

@app.route('/solve', methods=['POST'])
def solve():
    try:
        question = request.form.get('question', '').lower()

        # Identify the Distribution
        if "binomial" in question:
            return binomial_distribution(question)
        elif "poisson" in question:
            return poisson_distribution(question)
        elif "normal" in question:
            return normal_distribution(question)
        elif "exponential" in question:
            return exponential_distribution(question)
        elif "uniform" in question:
            return uniform_distribution(question)
        elif "geometric" in question:
            return geometric_distribution(question)
        else:
            return render_template_string(html_template, result="❌ Could not detect a valid distribution.", steps="")

    except Exception as e:
        return render_template_string(html_template, result=f"⚠️ Error: {str(e)}", steps="")

# **Binomial Distribution Function**
def binomial_distribution(question):
    mean_match = re.search(r'mean[ =](\d+)', question)
    variance_match = re.search(r'variance[ =](\d+)', question)
    x_match = re.search(r'(\d+)', question)
    at_least = "at least" in question

    if mean_match and variance_match and x_match:
        mu = float(mean_match.group(1))
        sigma_sq = float(variance_match.group(1))
        x = int(x_match.group(1))
        
        n = round(mu**2 / (mu - sigma_sq))
        p = mu / n
        prob = 1 - sum(binom.pmf(i, n, p) for i in range(x)) if at_least else binom.pmf(x, n, p)

        steps = f"""
        Given: Mean (μ) = {mu}, Variance (σ²) = {sigma_sq}
        Step 1: Compute n = μ² / (μ - σ²) = {n}
        Step 2: Compute p = μ / n = {p:.4f}
        Step 3: Use Binomial formula.
        """
        return render_template_string(html_template, result=f"P(X {'≥' if at_least else '='} {x}) = {prob:.4f}", steps=steps)

# **Poisson Distribution**
def poisson_distribution(question):
    mean_match = re.search(r'mean[ =](\d+)', question)
    x_match = re.search(r'(\d+)', question)

    if mean_match and x_match:
        lam = float(mean_match.group(1))
        x = int(x_match.group(1))
        prob = poisson.pmf(x, lam)

        steps = f"""
        Given: Mean λ = {lam}
        Step 1: Compute P(X = {x}) using Poisson formula.
        """
        return render_template_string(html_template, result=f"P(X = {x}) = {prob:.4f}", steps=steps)

# **Normal Distribution**
def normal_distribution(question):
    mean_match = re.search(r'mean[ =](\d+)', question)
    std_dev_match = re.search(r'standard deviation[ =](\d+)', question)
    x_match = re.search(r'(\d+)', question)

    if mean_match and std_dev_match and x_match:
        mu = float(mean_match.group(1))
        sigma = float(std_dev_match.group(1))
        x = float(x_match.group(1))
        
        prob = norm.cdf(x, mu, sigma)
        steps = f"""
        Given: Mean μ = {mu}, Standard Deviation σ = {sigma}
        Step 1: Compute P(X ≤ {x}) using Normal CDF.
        """
        return render_template_string(html_template, result=f"P(X ≤ {x}) = {prob:.4f}", steps=steps)

# **Exponential Distribution**
def exponential_distribution(question):
    mean_match = re.search(r'mean\s*([=\s]*)(\d+)', question)
    at_least_match = re.search(r'at\s*least\s*(\d+)', question)

    if mean_match:
        mean = float(mean_match.group(2))
        lambd = 1 / mean
        
        steps = f"Given Mean (μ) = {mean}, λ = 1/μ = {lambd:.6f}\n"

        if at_least_match:
            x = float(at_least_match.group(1))
            prob = math.exp(-lambd * x)
            steps += f"Compute P(X ≥ {x}) = e^(-λx) = {prob:.4f}\n"
            return render_template_string(html_template, result=f"P(X ≥ {x}) = {prob:.4f}", steps=steps)

    return render_template_string(html_template, result="❌ Invalid input for Exponential distribution.", steps="")

# **Uniform Distribution**
def uniform_distribution(question):
    min_match = re.search(r'minimum[ =](\d+)', question)
    max_match = re.search(r'maximum[ =](\d+)', question)
    x_match = re.search(r'(\d+)', question)

    if min_match and max_match and x_match:
        a = float(min_match.group(1))
        b = float(max_match.group(1))
        x = float(x_match.group(1))

        if a <= x <= b:
            prob = (x - a) / (b - a)
            steps = f"""
            Given: Min = {a}, Max = {b}
            Step 1: Compute P(X ≤ {x}) = (x - a) / (b - a)
            """
            return render_template_string(html_template, result=f"P(X ≤ {x}) = {prob:.4f}", steps=steps)

# **Geometric Distribution**
def geometric_distribution(question):
    p_match = re.search(r'p[ =](\d+\.?\d*)', question)
    x_match = re.search(r'x[ =](\d+)', question)

    if p_match and x_match:
        p = float(p_match.group(1))
        x = int(x_match.group(1))

        prob = geom.pmf(x, p)
        steps = f"""
        Given: Probability p = {p}, Trials x = {x}
        Step 1: Use Geometric PMF formula.
        """
        return render_template_string(html_template, result=f"P(X = {x}) = {prob:.4f}", steps=steps)

if __name__ == '__main__':
    app.run(debug=True)
