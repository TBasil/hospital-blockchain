import json
import tkinter as tk
from tkinter import ttk, messagebox
from core.blockchain import HealthcareBlockchain
from core.transaction import MedicalTransaction

class BlockchainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Blockchain System")
        self.root.geometry("900x600")
        
        self.blockchain = HealthcareBlockchain()
        self.create_widgets()
        self.update_chain_display()
    
    def create_widgets(self):
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Transaction Tab
        self.transaction_frame = ttk.Frame(self.notebook)
        self.create_transaction_tab()
        self.notebook.add(self.transaction_frame, text="Add Transaction")
        
        # Mine Tab
        self.mine_frame = ttk.Frame(self.notebook)
        self.create_mine_tab()
        self.notebook.add(self.mine_frame, text="Mine Block")
        
        # Blockchain Viewer Tab
        self.chain_frame = ttk.Frame(self.notebook)
        self.create_chain_tab()
        self.notebook.add(self.chain_frame, text="View Blockchain")
    
    def create_transaction_tab(self):
        # Patient Info
        ttk.Label(self.transaction_frame, text="Patient ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.patient_id = ttk.Entry(self.transaction_frame, width=40)
        self.patient_id.grid(row=0, column=1, padx=5, pady=5)
        
        # Doctor Info
        ttk.Label(self.transaction_frame, text="Doctor ID:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.doctor_id = ttk.Entry(self.transaction_frame, width=40)
        self.doctor_id.grid(row=1, column=1, padx=5, pady=5)
        
        # Record Type
        ttk.Label(self.transaction_frame, text="Record Type:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.record_type = ttk.Combobox(self.transaction_frame, values=["diagnosis", "prescription", "lab_result"])
        self.record_type.grid(row=2, column=1, padx=5, pady=5)
        
        # Medical Data
        ttk.Label(self.transaction_frame, text="Medical Data (JSON format):").grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        self.medical_data = tk.Text(self.transaction_frame, width=40, height=10)
        self.medical_data.grid(row=3, column=1, padx=5, pady=5)
        
        # Example button
        ttk.Button(
            self.transaction_frame, 
            text="Insert Example", 
            command=self.insert_example
        ).grid(row=4, column=0, pady=5, sticky="e")
        
        # Submit Button
        ttk.Button(
            self.transaction_frame, 
            text="Add Transaction", 
            command=self.add_transaction
        ).grid(row=4, column=1, pady=10, sticky="e")
    
    def create_mine_tab(self):
        # Mining Info
        ttk.Label(self.mine_frame, text="Pending Transactions:").pack(pady=(10,0))
        self.pending_transactions = tk.Listbox(self.mine_frame, height=10, width=100)
        self.pending_transactions.pack(pady=5, padx=10, fill=tk.BOTH)
        
        # Mine Button
        ttk.Button(self.mine_frame, text="Mine Block", command=self.mine_block).pack(pady=10)
        
        # Status Label
        self.mining_status = ttk.Label(self.mine_frame, text="Ready to mine")
        self.mining_status.pack()
        
        self.update_pending_transactions()
    
    def create_chain_tab(self):
        # Blockchain Treeview
        self.chain_tree = ttk.Treeview(
            self.chain_frame, 
            columns=("Index", "Timestamp", "Transactions", "Previous Hash"), 
            show="headings"
        )
        self.chain_tree.heading("Index", text="Block Index")
        self.chain_tree.heading("Timestamp", text="Timestamp")
        self.chain_tree.heading("Transactions", text="Transaction Count")
        self.chain_tree.heading("Previous Hash", text="Previous Hash")
        self.chain_tree.column("Index", width=50)
        self.chain_tree.column("Timestamp", width=150)
        self.chain_tree.column("Transactions", width=100)
        self.chain_tree.column("Previous Hash", width=200)
        self.chain_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh Button
        ttk.Button(self.chain_frame, text="Refresh", command=self.update_chain_display).pack(pady=10)
    
    def insert_example(self):
        example_data = """{
    "condition": "Hypertension",
    "severity": "Stage 1",
    "notes": "Patient needs regular monitoring"
}"""
        self.medical_data.delete("1.0", tk.END)
        self.medical_data.insert("1.0", example_data)
    
    def add_transaction(self):
        try:
            # Get raw medical data
            raw_data = self.medical_data.get("1.0", tk.END).strip()
            
            # Handle empty medical data
            if not raw_data:
                raise ValueError("Medical data cannot be empty")
            
            # Try to parse JSON
            try:
                medical_dict = json.loads(raw_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {str(e)}")
            
            # Validate required fields
            if not all([self.patient_id.get(), self.doctor_id.get(), self.record_type.get()]):
                raise ValueError("All fields (Patient ID, Doctor ID, Record Type) are required")
            
            # Create transaction
            transaction = MedicalTransaction(
                patient_id=self.patient_id.get(),
                doctor_id=self.doctor_id.get(),
                record_type=self.record_type.get(),
                data=medical_dict
            )
            
            # Add to blockchain
            self.blockchain.add_transaction(transaction.to_dict())
            
            messagebox.showinfo("Success", "Transaction added to pending pool")
            self.update_pending_transactions()
            self.clear_transaction_fields()
            
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Could not add transaction:\n\n{str(e)}\n\n"
                "Please ensure:\n"
                "1. All fields are filled\n"
                "2. Medical data is valid JSON\n"
                "3. Data matches the expected format"
            )
    
    def mine_block(self):
        block = self.blockchain.mine_block()
        if block:
            messagebox.showinfo("Success", f"New block mined! Index: {block.index}")
            self.update_pending_transactions()
            self.update_chain_display()
        else:
            messagebox.showwarning("Warning", "No transactions to mine")
    
    def update_pending_transactions(self):
        self.pending_transactions.delete(0, tk.END)
        for tx in self.blockchain.current_transactions:
            self.pending_transactions.insert(
                tk.END, 
                f"{tx['record_type']} - Patient: {tx['patient_id']} - Data: {str(tx['data'])[:50]}..."
            )
    
    def update_chain_display(self):
        for item in self.chain_tree.get_children():
            self.chain_tree.delete(item)
            
        for block in self.blockchain.chain:
            self.chain_tree.insert("", tk.END, values=(
                block.index,
                block.timestamp,
                len(block.transactions),
                block.previous_hash[:20] + "..." if block.previous_hash else "None"
            ))
    
    def clear_transaction_fields(self):
        self.patient_id.delete(0, tk.END)
        self.doctor_id.delete(0, tk.END)
        self.record_type.set('')
        self.medical_data.delete("1.0", tk.END)

def run_gui():
    root = tk.Tk()
    app = BlockchainApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()