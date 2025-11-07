
import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import remarkGfm from 'remark-gfm';

// Professional color palette with complementary and analogous colors
const COLORS = [
    '#4f46e5', // deep indigo (Income)
    '#16a34a', // rich green (Groceries)
    '#9333ea', // deep purple (Subscriptions)
    '#e11d48', // crimson (Restaurants)
    '#d97706', // dark amber (Shopping)
    '#0369a1', // strong blue (Transport)
    '#4338ca', // royal purple (Utilities)
    '#15803d', // forest green (Travel)
    '#be185d', // rich pink (Housing)
    '#334155', // slate blue (Uncategorized)
];

function App() {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [chatHistory, setChatHistory] = useState([]);
    const [userInput, setUserInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [showNewTransactionModal, setShowNewTransactionModal] = useState(false);
    const [newTransaction, setNewTransaction] = useState({
        date: new Date().toISOString().split('T')[0],
        description: '',
        amount: '',
        category: ''
    });

    useEffect(() => {
        const fetchTransactions = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await fetch('/api/transactions');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status} ${response.statusText}`);
                }
                const data = await response.json();
                setTransactions(data);
            } catch (e) {
                setError(`Failed to fetch transactions: ${e.message}. Please check if the backend is running.`);
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchTransactions();
    }, []);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!userInput.trim() || isTyping) return;

        const newHistory = [...chatHistory, { role: 'user', text: userInput }];
        setChatHistory(newHistory);
        setUserInput('');
        setIsTyping(true);

        try {
            // send a single description as expected by the backend CategorizationRequest
            const response = await fetch('/api/categorize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description: userInput }),
            });
            if (!response.ok) {
                // capture validation errors (422) and others
                const txt = await response.text();
                throw new Error(`API error! status: ${response.status} ${txt}`);
            }
            const data = await response.json();
            const assistantText = `Category: **${data.category}** (confidence: ${(data.confidence ?? 0).toFixed(2)})`;
            setChatHistory([...newHistory, { role: 'assistant', text: assistantText }]);
        } catch (error) {
            setChatHistory([...newHistory, { role: 'assistant', text: `Sorry, I encountered an error: ${error.message}` }]);
        } finally {
            setIsTyping(false);
        }
    };

    const categoryData = transactions.reduce((acc, t) => {
        const category = t.category || 'Uncategorized';
        if (!acc[category]) {
            acc[category] = 0;
        }
        acc[category] += t.amount;
        return acc;
    }, {});

    const pieData = Object.keys(categoryData).map(key => ({
        name: key,
        value: Math.abs(categoryData[key]),
    }));


    if (loading) {
        return <div className="app-shell"><div className="card">Loading dashboard...</div></div>;
    }

    if (error) {
        return <div className="app-shell"><div className="card"><pre className="muted">{error}</pre></div></div>;
    }

    return (
        <div className="app-shell">
            <div className="brand">
                <div className="logo">FW</div>
                <div>
                    <h1>FinWiz</h1>
                    <p className="muted">Your AI-Powered Personal Finance Advisor</p>
                </div>
            </div>

            <div className="grid">
                <div>
                    <div className="card">
                        <h2>Spending Overview</h2>
                        <div style={{height:300}}>
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie 
                                        data={pieData} 
                                        cx="50%" 
                                        cy="50%" 
                                        outerRadius={100} 
                                        fill="#8884d8" 
                                        dataKey="value" 
                                        nameKey="name"
                                    >
                                        {pieData.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                                    </Pie>
                                    <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                                    <Legend layout="vertical" align="right" verticalAlign="middle" />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    <div className="card" style={{marginTop:16}}>
                        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>
                            <h2>Recent Transactions</h2>
                            <button className="primary" onClick={() => setShowNewTransactionModal(true)}>+ Add Transaction</button>
                        </div>
                        {showNewTransactionModal && (
                            <div className="modal">
                                <div className="modal-content card">
                                    <h3>Add New Transaction</h3>
                                    <form onSubmit={async (e) => {
                                        e.preventDefault();
                                        try {
                                            const response = await fetch('/api/transactions', {
                                                method: 'POST',
                                                headers: { 'Content-Type': 'application/json' },
                                                body: JSON.stringify({
                                                    ...newTransaction,
                                                    amount: parseFloat(newTransaction.amount)
                                                })
                                            });
                                            if (!response.ok) throw new Error('Failed to add transaction');
                                            const result = await response.json();
                                            setTransactions([...transactions, result]);
                                            setShowNewTransactionModal(false);
                                            setNewTransaction({
                                                date: new Date().toISOString().split('T')[0],
                                                description: '',
                                                amount: '',
                                                category: ''
                                            });
                                        } catch (err) {
                                            console.error('Failed to add transaction:', err);
                                        }
                                    }}>
                                        <div className="form-group">
                                            <label>Date</label>
                                            <input
                                                type="date"
                                                value={newTransaction.date}
                                                onChange={e => setNewTransaction({...newTransaction, date: e.target.value})}
                                                required
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Description</label>
                                            <input
                                                type="text"
                                                value={newTransaction.description}
                                                onChange={e => setNewTransaction({...newTransaction, description: e.target.value})}
                                                required
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Amount</label>
                                            <input
                                                type="number"
                                                step="0.01"
                                                value={newTransaction.amount}
                                                onChange={e => setNewTransaction({...newTransaction, amount: e.target.value})}
                                                required
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Category</label>
                                            <select
                                                value={newTransaction.category}
                                                onChange={e => setNewTransaction({...newTransaction, category: e.target.value})}
                                                required
                                            >
                                                <option value="">Select a category...</option>
                                                <option value="Income">Income</option>
                                                <option value="Housing">Housing</option>
                                                <option value="Transport">Transport</option>
                                                <option value="Groceries">Groceries</option>
                                                <option value="Utilities">Utilities</option>
                                                <option value="Shopping">Shopping</option>
                                                <option value="Restaurants">Restaurants</option>
                                                <option value="Travel">Travel</option>
                                                <option value="Subscriptions">Subscriptions</option>
                                            </select>
                                        </div>
                                        <div className="form-actions">
                                            <button type="button" className="secondary" onClick={() => setShowNewTransactionModal(false)}>Cancel</button>
                                            <button type="submit" className="primary">Add Transaction</button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        )}
                        <div style={{overflowX:'auto'}}>
                            <table className="transactions-table">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Description</th>
                                        <th>Category</th>
                                        <th style={{textAlign:'right'}}>Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {transactions.map(t => (
                                        <tr key={t.id}>
                                            <td>{t.date}</td>
                                            <td>{t.description}</td>
                                            <td><span className={`badge ${t.category ? t.category.toLowerCase().replace(/\s+/g,'') : 'uncategorized'}`}>{t.category || 'N/A'}</span></td>
                                            <td className="amount">${Math.abs(t.amount).toFixed(2)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <aside>
                    <div className="card chat">
                        <h3>AI Advisor</h3>
                        <div className="chat-history">
                            {chatHistory.map((msg, index) => (
                                <div key={index} style={{display:'flex',justifyContent: msg.role==='user' ? 'flex-end':'flex-start'}}>
                                    <div style={{maxWidth:360,background: msg.role==='user' ? 'linear-gradient(90deg,var(--accent),var(--accent-2))' : 'rgba(255,255,255,0.03)',color: msg.role==='user' ? '#042046': 'var(--text)',padding:10,borderRadius:10,marginBottom:8}}>
                                        <div className="prose prose-invert prose-sm">
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {isTyping && <div className="muted">Thinking...</div>}
                        </div>
                        <form onSubmit={handleSendMessage} className="chat-input">
                            <input type="text" value={userInput} onChange={(e)=>setUserInput(e.target.value)} placeholder="Ask about your finances..." disabled={isTyping} />
                            <button type="submit" disabled={isTyping}>Send</button>
                        </form>
                    </div>
                </aside>
            </div>

        </div>
    );
}

export default App;
