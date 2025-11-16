from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from datetime import datetime
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'AIzaSyCuz7HJH4sRvj5miAIPcrZ8t3tKwULOIbo'

# Data storage files
STUDENTS_FILE = 'students.json'
FEES_FILE = 'fees.json'
PAYMENTS_FILE = 'payments.json'
USERS_FILE = 'users.json'

# Initialize data files
def init_data_files():
    if not os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, 'w') as f:
            json.dump([], f) 
    if not os.path.exists(FEES_FILE):
        with open(FEES_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(PAYMENTS_FILE):
        with open(PAYMENTS_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([{'username': 'admin', 'password': 'admin123', 'role': 'admin'}], f)

# Helper functions

def load_data(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# HTML Template

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Fee Management System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(to bottom, #ffffff 0%, #666699 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: #F5F5DC;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            color: #667eea;
            font-size: 2em;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-success {
            background: #10b981;
            color: white;
        }

        .btn-danger {
            background: #ef4444;
            color: white;
        }

        .btn-warning {
            background: #f59e0b;
            color: white;
        }

        .btn-info {
            background:#C71585;
            color: white;
        }

        .tabs {
            background: white;
            border-radius: 15px;
            padding: 10px;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            flex-wrap: wrap;
        }

        .tab {
            padding: 15px 30px;
            border: none;
            background: transparent;
            color: #8B008B;
            cursor: pointer;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .tab.active {
            background: linear-gradient(to top left, #0099cc 0%, #ffff99 100%);
            color: #4B0082;
        }

        .content {
            background: #E6E6FA;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            display: none;
        }

        .content.active {
            display: block;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }

        .form-group input,
        .form-group select {
            padding: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        table th {
            background: linear-gradient(to top left, #0099cc 0%, #ffff99 100%);
            color: #8B008B;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }

        table td {
            padding: 12px 15px;
            border-bottom: 1px solid #e5e7eb;
        }

        table tr:hover {
            background: #f9fafb;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 15px;
            color: white;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }

        .stat-card h3 {
            font-size: 14px;
            margin-bottom: 10px;
            opacity: 0.9;
        }

        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
        }

        .search-box {
            padding: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            width: 100%;
            max-width: 400px;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .badge-success {
            background: #d1fae5;
            color: #065f46;
        }

        .badge-danger {
            background: #fee2e2;
            color: #991b1b;
        }

        .badge-warning {
            background: #fef3c7;
            color: #92400e;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 500px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .close {
            font-size: 28px;
            cursor: pointer;
            color: #999;
        }

        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .alert-success {
            background: #d1fae5;
            color: #065f46;
        }

        .alert-error {
            background: #fee2e2;
            color: #991b1b;
        }

        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 15px;
            }

            .tabs {
                flex-direction: column;
            }

            table {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 + 💵 Student Fee Management System</h1>
            <div class="user-info">
                <span>Welcome, <strong>{{ session.user }}</strong></span>
                <a href="/logout" class="btn btn-danger">Logout</a>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('dashboard')">Dashboard</button>
            <button class="tab" onclick="showTab('students')">Students</button>
            <button class="tab" onclick="showTab('fees')">Fee Structure</button>
            <button class="tab" onclick="showTab('payments')">Payments</button>
            <button class="tab" onclick="showTab('reports')">Reports</button>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="content active">
            <h2>Dashboard</h2>
            <div class="stats" id="stats"></div>
            <h3>Recent Payments</h3>
            <table id="recentPayments">
                <thead>
                    <tr>
                        <th>Student ID</th>
                        <th>Student Name</th>
                        <th>Amount</th>
                        <th>Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>

        <!-- Students Tab -->
        <div id="students" class="content">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2>Student Management</h2>
                <button class="btn btn-primary" onclick="showAddStudentModal()">+ Add Student</button>
            </div>
            <input type="text" class="search-box" placeholder="Search students..." onkeyup="searchStudents(this.value)">
            <table id="studentsTable">
                <thead>
                    <tr>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Course</th>
                        <th>Year</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>

        <!-- Fees Tab -->
        <div id="fees" class="content">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2>Fee Structure</h2>
                <button class="btn btn-primary" onclick="showAddFeeModal()">+ Add Fee Type</button>
            </div>
            <table id="feesTable">
                <thead>
                    <tr>
                        <th>Fee Type</th>
                        <th>Course</th>
                        <th>Year</th>
                        <th>Amount</th>
                        <th>Due Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>

        <!-- Payments Tab -->
        <div id="payments" class="content">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2>Payment Management</h2>
                <button class="btn btn-success" onclick="showAddPaymentModal()">+ Record Payment</button>
            </div>
            <input type="text" class="search-box" placeholder="Search payments..." onkeyup="searchPayments(this.value)">
            <table id="paymentsTable">
                <thead>
                    <tr>
                        <th>Payment ID</th>
                        <th>Student ID</th>
                        <th>Student Name</th>
                        <th>Fee Type</th>
                        <th>Amount</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>

        <!-- Reports Tab -->
        <div id="reports" class="content">
            <h2>Reports & Analytics</h2>
            <div class="stats" id="reportStats"></div>
            <div style="margin-top: 30px;">
                <h3>Generate Reports</h3>
                <div class="form-grid">
                    <button class="btn btn-info" onclick="generateReport('defaulters')">Defaulters Report</button>
                    <button class="btn btn-info" onclick="generateReport('collected')">Collection Report</button>
                    <button class="btn btn-info" onclick="generateReport('pending')">Pending Payments</button>
                    <button class="btn btn-info" onclick="generateReport('course')">Course-wise Report</button>
                </div>
            </div>
            <div id="reportContent" style="margin-top: 20px;"></div>
        </div>
    </div>

    <!-- Add Student Modal -->
    <div id="addStudentModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Add New Student</h2>
                <span class="close" onclick="closeModal('addStudentModal')">&times;</span>
            </div>
            <form id="addStudentForm">
                <div class="form-group">
                    <label>Student ID</label>
                    <input type="text" name="student_id" required>
                </div>
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Phone</label>
                    <input type="tel" name="phone" required>
                </div>
                <div class="form-group">
                    <label>Course</label>
                    <input type="text" name="course" required>
                </div>
                <div class="form-group">
                    <label>Year</label>
                    <select name="year" required>
                        <option value="1">1st Year</option>
                        <option value="2">2nd Year</option>
                        <option value="3">3rd Year</option>
                        <option value="4">4th Year</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Add Student</button>
            </form>
        </div>
    </div>

    <!-- Add Fee Modal -->
    <div id="addFeeModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Add Fee Structure</h2>
                <span class="close" onclick="closeModal('addFeeModal')">&times;</span>
            </div>
            <form id="addFeeForm">
                <div class="form-group">
                    <label>Fee Type</label>
                    <input type="text" name="fee_type" placeholder="e.g., Tuition Fee, Lab Fee" required>
                </div>
                <div class="form-group">
                    <label>Course</label>
                    <input type="text" name="course" required>
                </div>
                <div class="form-group">
                    <label>Year</label>
                    <select name="year" required>
                        <option value="1">1st Year</option>
                        <option value="2">2nd Year</option>
                        <option value="3">3rd Year</option>
                        <option value="4">4th Year</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Amount (₹)</label>
                    <input type="number" name="amount" required>
                </div>
                <div class="form-group">
                    <label>Due Date</label>
                    <input type="date" name="due_date" required>
                </div>
                <button type="submit" class="btn btn-primary">Add Fee</button>
            </form>
        </div>
    </div>

    <!-- Add Payment Modal -->
    <div id="addPaymentModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Record Payment</h2>
                <span class="close" onclick="closeModal('addPaymentModal')">&times;</span>
            </div>
            <form id="addPaymentForm">
                <div class="form-group">
                    <label>Student ID</label>
                    <input type="text" name="student_id" required>
                </div>
                <div class="form-group">
                    <label>Fee Type</label>
                    <select name="fee_type" id="feeTypeSelect" required></select>
                </div>
                <div class="form-group">
                    <label>Amount (₹)</label>
                    <input type="number" name="amount" required>
                </div>
                <div class="form-group">
                    <label>Payment Date</label>
                    <input type="date" name="payment_date" required>
                </div>
                <div class="form-group">
                    <label>Payment Method</label>
                    <select name="payment_method" required>
                        <option value="Cash">Cash</option>
                        <option value="Online">Online</option>
                        <option value="Cheque">Cheque</option>
                        <option value="Card">Card</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-success">Record Payment</button>
            </form>
        </div>
    </div>

    <script>
        let students = [];
        let fees = [];
        let payments = [];

        function showTab(tabName) {
            document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'dashboard') loadDashboard();
            if (tabName === 'students') loadStudents();
            if (tabName === 'fees') loadFees();
            if (tabName === 'payments') loadPayments();
            if (tabName === 'reports') loadReports();
        }

        function showAddStudentModal() {
            document.getElementById('addStudentModal').classList.add('active');
        }

        function showAddFeeModal() {
            document.getElementById('addFeeModal').classList.add('active');
        }

        function showAddPaymentModal() {
            loadFeeTypes();
            document.getElementById('addPaymentModal').classList.add('active');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
        }

        async function loadDashboard() {
            const response = await fetch('/api/dashboard');
            const data = await response.json();
            
            document.getElementById('stats').innerHTML = `
                <div class="stat-card">
                    <h3>Total Students</h3>
                    <div class="value">${data.total_students}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Collection</h3>
                    <div class="value">₹${data.total_collected.toLocaleString()}</div>
                </div>
                <div class="stat-card">
                    <h3>Pending Amount</h3>
                    <div class="value">₹${data.pending_amount.toLocaleString()}</div>
                </div>
                <div class="stat-card">
                    <h3>Defaulters</h3>
                    <div class="value">${data.defaulters}</div>
                </div>
            `;

            const tbody = document.querySelector('#recentPayments tbody');
            tbody.innerHTML = data.recent_payments.map(p => `
                <tr>
                    <td>${p.student_id}</td>
                    <td>${p.student_name}</td>
                    <td>₹${p.amount.toLocaleString()}</td>
                    <td>${p.payment_date}</td>
                    <td><span class="badge badge-success">Paid</span></td>
                </tr>
            `).join('');
        }

        async function loadStudents() {
            const response = await fetch('/api/students');
            students = await response.json();
            displayStudents(students);
        }

        function displayStudents(data) {
            const tbody = document.querySelector('#studentsTable tbody');
            tbody.innerHTML = data.map(s => `
                <tr>
                    <td>${s.student_id}</td>
                    <td>${s.name}</td>
                    <td>${s.email}</td>
                    <td>${s.phone}</td>
                    <td>${s.course}</td>
                    <td>${s.year}</td>
                    <td>
                        <button class="btn btn-warning" onclick="deleteStudent('${s.student_id}')">Delete</button>
                    </td>
                </tr>
            `).join('');
        }

        function searchStudents(query) {
            const filtered = students.filter(s => 
                s.student_id.toLowerCase().includes(query.toLowerCase()) ||
                s.name.toLowerCase().includes(query.toLowerCase()) ||
                s.email.toLowerCase().includes(query.toLowerCase())
            );
            displayStudents(filtered);
        }

        async function loadFees() {
            const response = await fetch('/api/fees');
            fees = await response.json();
            displayFees(fees);
        }

        function displayFees(data) {
            const tbody = document.querySelector('#feesTable tbody');
            tbody.innerHTML = data.map(f => `
                <tr>
                    <td>${f.fee_type}</td>
                    <td>${f.course}</td>
                    <td>${f.year}</td>
                    <td>₹${f.amount.toLocaleString()}</td>
                    <td>${f.due_date}</td>
                    <td>
                        <button class="btn btn-danger" onclick="deleteFee('${f.id}')">Delete</button>
                    </td>
                </tr>
            `).join('');
        }

        async function loadPayments() {
            const response = await fetch('/api/payments');
            payments = await response.json();
            displayPayments(payments);
        }

        function displayPayments(data) {
            const tbody = document.querySelector('#paymentsTable tbody');
            tbody.innerHTML = data.map(p => `
                <tr>
                    <td>${p.payment_id}</td>
                    <td>${p.student_id}</td>
                    <td>${p.student_name}</td>
                    <td>${p.fee_type}</td>
                    <td>₹${p.amount.toLocaleString()}</td>
                    <td>${p.payment_date}</td>
                    <td><span class="badge badge-success">${p.status}</span></td>
                    <td>
                        <button class="btn btn-info" onclick="printReceipt('${p.payment_id}')">Receipt</button>
                    </td>
                </tr>
            `).join('');
        }

        function searchPayments(query) {
            const filtered = payments.filter(p => 
                p.student_id.toLowerCase().includes(query.toLowerCase()) ||
                p.student_name.toLowerCase().includes(query.toLowerCase()) ||
                p.fee_type.toLowerCase().includes(query.toLowerCase())
            );
            displayPayments(filtered);
        }

        async function loadFeeTypes() {
            const response = await fetch('/api/fees');
            const feesList = await response.json();
            const select = document.getElementById('feeTypeSelect');
            select.innerHTML = feesList.map(f => 
                `<option value="${f.fee_type}">${f.fee_type} - ${f.course} (Year ${f.year})</option>`
            ).join('');
        }

        async function loadReports() {
            const response = await fetch('/api/dashboard');
            const data = await response.json();
            
            document.getElementById('reportStats').innerHTML = `
                <div class="stat-card">
                    <h3>Collection Rate</h3>
                    <div class="value">${data.collection_rate}%</div>
                </div>
                <div class="stat-card">
                    <h3>Average Fee/Student</h3>
                    <div class="value">₹${data.avg_fee_per_student.toLocaleString()}</div>
                </div>
                <div class="stat-card">
                    <h3>This Month Collection</h3>
                    <div class="value">₹${data.month_collection.toLocaleString()}</div>
                </div>
            `;
        }

        async function generateReport(type) {
            const response = await fetch(`/api/report/${type}`);
            const data = await response.json();
            const reportContent = document.getElementById('reportContent');
            
            reportContent.innerHTML = `
                <h3>${data.title}</h3>
                <table>
                    <thead>
                        <tr>${data.headers.map(h => `<th>${h}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${data.rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}
                    </tbody>
                </table>
            `;
        }

        document.getElementById('addStudentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            const response = await fetch('/api/students', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                closeModal('addStudentModal');
                loadStudents();
                e.target.reset();
                alert('Student added successfully!');
            }
        });

        document.getElementById('addFeeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            const response = await fetch('/api/fees', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                closeModal('addFeeModal');
                loadFees();
                e.target.reset();
                alert('Fee structure added successfully!');
            }
        });

        document.getElementById('addPaymentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            const response = await fetch('/api/payments', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                closeModal('addPaymentModal');
                loadPayments();
                e.target.reset();
                alert('Payment recorded successfully!');
            }
        });

        async function deleteStudent(studentId) {
            if (confirm('Are you sure you want to delete this student?')) {
                await fetch(`/api/students/${studentId}`, {method: 'DELETE'});
                loadStudents();
            }
        }

        async function deleteFee(feeId) {
            if (confirm('Are you sure you want to delete this fee?')) {
                await fetch(`/api/fees/${feeId}`, {method: 'DELETE'});
                loadFees();
            }
        }

        function printReceipt(paymentId) {
            window.open(`/receipt/${paymentId}`, '_blank');
        }

        loadDashboard();
    </script>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - Fee Management System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            width: 400px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 30px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .error {
            color: #ef4444;
            margin-top: 10px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🎓 Fee Management</h1>
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Login</button>
            {% if error %}
            <p class="error">{{ error }}</p>
            {% endif %}
        </form>
        <p style="margin-top: 20px; text-align: center; color: #666; font-size: 12px;">
            Default credentials: admin / admin123
        </p>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
@login_required
def index():
    return render_template_string(HTML_TEMPLATE, session=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_data(USERS_FILE)
        
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['user'] = username
            session['role'] = user['role']
            return redirect(url_for('index'))
        return render_template_string(LOGIN_TEMPLATE, error='Invalid credentials')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/dashboard')
@login_required
def get_dashboard():
    students = load_data(STUDENTS_FILE)
    payments = load_data(PAYMENTS_FILE)
    fees = load_data(FEES_FILE)
    
    total_collected = sum(p['amount'] for p in payments)
    total_fees = sum(f['amount'] for f in fees) * len(students)
    pending = total_fees - total_collected
    
    recent_payments = sorted(payments, key=lambda x: x['payment_date'], reverse=True)[:5]
    
    return jsonify({
        'total_students': len(students),
        'total_collected': total_collected,
        'pending_amount': pending,
        'defaulters': len([s for s in students if not any(p['student_id'] == s['student_id'] for p in payments)]),
        'recent_payments': recent_payments,
        'collection_rate': round((total_collected / total_fees * 100) if total_fees > 0 else 0, 2),
        'avg_fee_per_student': round(total_collected / len(students)) if students else 0,
        'month_collection': sum(p['amount'] for p in payments if p['payment_date'].startswith(datetime.now().strftime('%Y-%m')))
    })

@app.route('/api/students', methods=['GET', 'POST'])
@login_required
def manage_students():
    if request.method == 'POST':
        students = load_data(STUDENTS_FILE)
        student = request.json
        students.append(student)
        save_data(STUDENTS_FILE, students)
        return jsonify({'success': True})
    
    return jsonify(load_data(STUDENTS_FILE))

@app.route('/api/students/<student_id>', methods=['DELETE'])
@login_required
def delete_student(student_id):
    students = load_data(STUDENTS_FILE)
    students = [s for s in students if s['student_id'] != student_id]
    save_data(STUDENTS_FILE, students)
    return jsonify({'success': True})

@app.route('/api/fees', methods=['GET', 'POST'])
@login_required
def manage_fees():
    if request.method == 'POST':
        fees = load_data(FEES_FILE)
        fee = request.json
        fee['id'] = f"FEE{len(fees) + 1:04d}"
        fees.append(fee)
        save_data(FEES_FILE, fees)
        return jsonify({'success': True})
    
    return jsonify(load_data(FEES_FILE))

@app.route('/api/fees/<fee_id>', methods=['DELETE'])
@login_required
def delete_fee(fee_id):
    fees = load_data(FEES_FILE)
    fees = [f for f in fees if f['id'] != fee_id]
    save_data(FEES_FILE, fees)
    return jsonify({'success': True})

@app.route('/api/payments', methods=['GET', 'POST'])
@login_required
def manage_payments():
    if request.method == 'POST':
        payments = load_data(PAYMENTS_FILE)
        students = load_data(STUDENTS_FILE)
        payment = request.json
        
        student = next((s for s in students if s['student_id'] == payment['student_id']), None)
        if student:
            payment['payment_id'] = f"PAY{len(payments) + 1:06d}"
            payment['student_name'] = student['name']
            payment['status'] = 'Paid'
            payments.append(payment)
            save_data(PAYMENTS_FILE, payments)
            return jsonify({'success': True})
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify(load_data(PAYMENTS_FILE))

@app.route('/api/report/<report_type>')
@login_required
def generate_report(report_type):
    students = load_data(STUDENTS_FILE)
    payments = load_data(PAYMENTS_FILE)
    fees = load_data(FEES_FILE)
    
    if report_type == 'defaulters':
        paid_students = set(p['student_id'] for p in payments)
        defaulters = [s for s in students if s['student_id'] not in paid_students]
        return jsonify({
            'title': 'Defaulters Report',
            'headers': ['Student ID', 'Name', 'Course', 'Year', 'Contact'],
            'rows': [[d['student_id'], d['name'], d['course'], d['year'], d['phone']] for d in defaulters]
        })
    
    elif report_type == 'collected':
        return jsonify({
            'title': 'Collection Report',
            'headers': ['Student ID', 'Student Name', 'Fee Type', 'Amount', 'Date'],
            'rows': [[p['student_id'], p['student_name'], p['fee_type'], f"₹{p['amount']}", p['payment_date']] for p in payments]
        })
    
    elif report_type == 'pending':
        paid_students = set(p['student_id'] for p in payments)
        pending = []
        for student in students:
            total_fees = sum(f['amount'] for f in fees if f['course'] == student['course'] and str(f['year']) == str(student['year']))
            paid = sum(p['amount'] for p in payments if p['student_id'] == student['student_id'])
            if paid < total_fees:
                pending.append([student['student_id'], student['name'], f"₹{total_fees}", f"₹{paid}", f"₹{total_fees - paid}"])
        return jsonify({
            'title': 'Pending Payments Report',
            'headers': ['Student ID', 'Name', 'Total Fees', 'Paid', 'Pending'],
            'rows': pending
        })
    
    elif report_type == 'course':
        course_data = {}
        for payment in payments:
            student = next((s for s in students if s['student_id'] == payment['student_id']), None)
            if student:
                course = student['course']
                if course not in course_data:
                    course_data[course] = 0
                course_data[course] += payment['amount']
        
        return jsonify({
            'title': 'Course-wise Collection Report',
            'headers': ['Course', 'Total Collection', 'Student Count'],
            'rows': [[course, f"₹{amount}", len([s for s in students if s['course'] == course])] 
                    for course, amount in course_data.items()]
        })
    
    return jsonify({'error': 'Invalid report type'}), 400

@app.route('/receipt/<payment_id>')
@login_required
def receipt(payment_id):
    payments = load_data(PAYMENTS_FILE)
    payment = next((p for p in payments if p['payment_id'] == payment_id), None)
    
    if not payment:
        return "Receipt not found", 404
    
    receipt_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Receipt</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }}
            .receipt {{
                border: 2px solid #333;
                padding: 30px;
            }}
            h1 {{
                text-align: center;
                color: #667eea;
            }}
            .info {{
                margin: 20px 0;
            }}
            .row {{
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
            }}
            .label {{
                font-weight: bold;
            }}
            @media print {{
                button {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="receipt">
            <h1>🎓 PAYMENT RECEIPT</h1>
            <hr>
            <div class="info">
                <div class="row">
                    <span class="label">Receipt No:</span>
                    <span>{payment['payment_id']}</span>
                </div>
                <div class="row">
                    <span class="label">Date:</span>
                    <span>{payment['payment_date']}</span>
                </div>
                <div class="row">
                    <span class="label">Student ID:</span>
                    <span>{payment['student_id']}</span>
                </div>
                <div class="row">
                    <span class="label">Student Name:</span>
                    <span>{payment['student_name']}</span>
                </div>
                <div class="row">
                    <span class="label">Fee Type:</span>
                    <span>{payment['fee_type']}</span>
                </div>
                <div class="row">
                    <span class="label">Payment Method:</span>
                    <span>{payment['payment_method']}</span>
                </div>
                <hr>
                <div class="row" style="font-size: 20px;">
                    <span class="label">Amount Paid:</span>
                    <span>₹{payment['amount']}</span>
                </div>
            </div>
            <p style="text-align: center; margin-top: 50px;">Thank you for your payment!</p>
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="window.print()" style="padding: 10px 30px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">Print Receipt</button>
        </div>
    </body>
    </html>
    '''
    return receipt_html

if __name__ == '__main__':
    init_data_files()
    print("=" * 60)
    print("Student Fee Management System")
    print("=" * 60)
    print("Starting server...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    print("Default login credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("=" * 60) 
    app.run(debug=True, host='0.0.0.0', port=5000)