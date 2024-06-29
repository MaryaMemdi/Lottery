from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "secret_key"

file_name = "payments.xlsx"

# Load data from excel file
def load_data():
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
        if 'WonLottery' not in df.columns:
            df['WonLottery'] = False
        return df
    else:
        return pd.DataFrame(columns=["Name", "WonLottery"])

# Save data to excel file
def save_data(df):
    df.to_excel(file_name, index=False)

@app.route('/')
def index():
    df = load_data()
    month_columns = [col for col in df.columns if col.startswith('Month')]
    return render_template('index.html', users=df.to_dict('records'), months=month_columns)

@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    df = load_data()
    if name:
        new_user = {"Name": name, "WonLottery": False}
        for month in [col for col in df.columns if col.startswith('Month')]:
            new_user[month] = False
        df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
        save_data(df)
        flash("User added successfully!")
    return redirect(url_for('index'))

@app.route('/update/<name>/<month>')
def update_payment(name, month):
    df = load_data()
    df.loc[df["Name"] == name, month] = not df.loc[df["Name"] == name, month].values[0]
    save_data(df)
    return redirect(url_for('index'))

@app.route('/edit/<name>', methods=['GET', 'POST'])
def edit_user(name):
    df = load_data()
    if request.method == 'POST':
        new_name = request.form['new_name']
        if new_name:
            df.loc[df["Name"] == name, "Name"] = new_name
            save_data(df)
            flash("User name updated successfully!")
        return redirect(url_for('index'))
    user = df.loc[df["Name"] == name].to_dict('records')[0]
    return render_template('edit.html', user=user)

@app.route('/unpaid')
def unpaid():
    df = load_data()
    month_columns = [col for col in df.columns if col.startswith('Month')]
    unpaid_users = df[(df[month_columns] == False).any(axis=1)]
    return render_template('unpaid.html', users=unpaid_users.to_dict('records'))

@app.route('/lottery')
def lottery():
    df = load_data()
    month_columns = [col for col in df.columns if col.startswith('Month')]
    unpaid_users = df[(df[month_columns] == False).any(axis=1) & (df['WonLottery'] == False)]
    if not unpaid_users.empty:
        winner = unpaid_users.sample(n=1).iloc[0]
        df.loc[df["Name"] == winner["Name"], "WonLottery"] = True
        save_data(df)
        flash(f"The winner is {winner['Name']}!")
    else:
        flash("No users available for the lottery.")
    return redirect(url_for('index'))

@app.route('/reset_lottery', methods=['POST'])
def reset_lottery():
    df = load_data()
    df['WonLottery'] = False
    save_data(df)
    flash("Lottery reset successfully!")
    return redirect(url_for('index'))

@app.route('/lottery_list')
def lottery_list():
    df = load_data()
    month_columns = [col for col in df.columns if col.startswith('Month')]
    eligible_users = df[(df[month_columns] == False).any(axis=1) & (df['WonLottery'] == False)]
    return render_template('lottery_list.html', users=eligible_users.to_dict('records'))

@app.route('/edit_lottery_list', methods=['POST'])
def edit_lottery_list():
    df = load_data()
    name = request.form['name']
    action = request.form['action']
    if action == 'add':
        df.loc[df["Name"] == name, 'WonLottery'] = False
    elif action == 'remove':
        df.loc[df["Name"] == name, 'WonLottery'] = True
    save_data(df)
    flash(f"User {name} {'added to' if action == 'add' else 'removed from'} lottery list successfully!")
    return redirect(url_for('lottery_list'))

@app.route('/add_month', methods=['POST'])
def add_month():
    df = load_data()
    month_columns = [col for col in df.columns if col.startswith('Month')]
    new_month = f'Month{len(month_columns) + 1}'
    df[new_month] = False
    save_data(df)
    flash("New month added successfully!")
    return redirect(url_for('index'))

@app.route('/remove_month', methods=['POST'])
def remove_month():
    df = load_data()
    month_columns = [col for col in df.columns if col.startswith('Month')]
    if month_columns:
        df.drop(columns=[month_columns[-1]], inplace=True)
        save_data(df)
        flash("Last month removed successfully!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
