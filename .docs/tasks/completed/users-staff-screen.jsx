import { useState, useRef, useEffect } from "react";

const mockUsers = [
  { id: 1, display_name: "new suthu",       code: "U-LABSB9", role: "dfgd",        email: "sutharsan2@gmail.com",       contact_no: "",           status: "Active" },
  { id: 2, display_name: "test uma",         code: "U-QP5H9S", role: "Super Admin",  email: "a.umakaran1126@gmail.com",   contact_no: "",           status: "Active" },
  { id: 3, display_name: "Test Customer",    code: "U-QP5H9R", role: "Super Admin",  email: "reyeka2386@hadvar.com",      contact_no: "",           status: "Active" },
  { id: 4, display_name: "kvp",              code: "U-D91XIS", role: "Super Admin",  email: "vatelit979@hadvar.com",      contact_no: "",           status: "Inactive" },
  { id: 5, display_name: "Mr. UmakaranKK umak", code: "U-I4LI74", role: "Super Admin", email: "relepor245@binafex.com",  contact_no: "9477123456", status: "Active" },
  { id: 6, display_name: "Sarah Mitchell",   code: "U-XK2P01", role: "Sales Agent",  email: "sarah.m@vanguard.com",      contact_no: "9477654321", status: "Active" },
  { id: 7, display_name: "Rohan Perera",     code: "U-BT9Q33", role: "Team Lead",    email: "rohan.p@vanguard.com",      contact_no: "",           status: "Active" },
  { id: 8, display_name: "Nisha Fernando",   code: "U-CZ8R55", role: "Sales Agent",  email: "nisha.f@vanguard.com",      contact_no: "9471234567", status: "Inactive" },
];

const mockInvitations = [
  { id: 1, name: "Alex Johnson",  email: "alex.j@example.com",   role: "Sales Agent",  invited_by: "Admin User", invited_on: "2026-03-18 09:00", expires_at: "2026-03-21 09:00", resent_count: 0, status: "pending" },
  { id: 2, name: "Priya Sharma",  email: "priya.s@example.com",  role: "Team Lead",    invited_by: "Admin User", invited_on: "2026-03-15 14:30", expires_at: "2026-03-18 14:30", resent_count: 1, status: "expired" },
  { id: 3, name: "Daniel Cruz",   email: "daniel.c@example.com", role: "Sales Agent",  invited_by: "test uma",   invited_on: "2026-03-19 11:00", expires_at: "2026-03-22 11:00", resent_count: 0, status: "pending" },
];

const ChevronDown = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
    <path d="M4 6l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const ChevronRight = ({ size = 12 }) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
    <path d="M6 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const SearchIcon = () => (
  <svg width="15" height="15" viewBox="0 0 20 20" fill="none">
    <circle cx="8.5" cy="8.5" r="5.5" stroke="#9CA3AF" strokeWidth="1.5"/>
    <path d="M13.5 13.5L17 17" stroke="#9CA3AF" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const ListIcon = () => (
  <svg width="15" height="15" viewBox="0 0 20 20" fill="none">
    <rect x="2" y="4" width="16" height="2" rx="1" fill="currentColor"/>
    <rect x="2" y="9" width="16" height="2" rx="1" fill="currentColor"/>
    <rect x="2" y="14" width="16" height="2" rx="1" fill="currentColor"/>
  </svg>
);
const InviteIcon = () => (
  <svg width="14" height="14" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M10 6v8M6 10h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const HierarchyIcon = () => (
  <svg width="14" height="14" viewBox="0 0 20 20" fill="none">
    <rect x="7" y="1" width="6" height="4" rx="1" stroke="currentColor" strokeWidth="1.4"/>
    <rect x="1" y="14" width="6" height="4" rx="1" stroke="currentColor" strokeWidth="1.4"/>
    <rect x="13" y="14" width="6" height="4" rx="1" stroke="currentColor" strokeWidth="1.4"/>
    <path d="M10 5v4M10 9H4v5M10 9h6v5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
  </svg>
);
const TeamIcon = () => (
  <svg width="14" height="14" viewBox="0 0 20 20" fill="none">
    <circle cx="7" cy="6" r="3" stroke="currentColor" strokeWidth="1.4"/>
    <circle cx="14" cy="6" r="2" stroke="currentColor" strokeWidth="1.4"/>
    <path d="M1 17c0-3.314 2.686-5 6-5s6 1.686 6 5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
    <path d="M14 11c1.886 0 4 .9 4 3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
  </svg>
);
const DotsIcon = () => (
  <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
    <circle cx="4" cy="10" r="1.5" fill="currentColor"/>
    <circle cx="10" cy="10" r="1.5" fill="currentColor"/>
    <circle cx="16" cy="10" r="1.5" fill="currentColor"/>
  </svg>
);
const FilterIcon = () => (
  <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
    <path d="M3 5h14M6 10h8M9 15h2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const ColumnsIcon = () => (
  <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
    <rect x="2" y="3" width="6" height="14" rx="1" stroke="currentColor" strokeWidth="1.4"/>
    <rect x="12" y="3" width="6" height="14" rx="1" stroke="currentColor" strokeWidth="1.4"/>
  </svg>
);
const ExpandIcon = () => (
  <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
    <path d="M3 3h5M3 3v5M17 3h-5M17 3v5M3 17h5M3 17v-5M17 17h-5M17 17v-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const BellIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const GlobeIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" stroke="currentColor" strokeWidth="1.5"/>
  </svg>
);
const MoonIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const HomeIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
    <path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M9 21V12h6v9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const HamburgerIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);

const StatusBadge = ({ status }) => {
  const isActive = status === "Active";
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      padding: "3px 10px", borderRadius: 20, fontSize: 11, fontWeight: 600,
      background: isActive ? "#ECFDF5" : "#F3F4F6",
      color: isActive ? "#065F46" : "#6B7280",
      border: `1px solid ${isActive ? "#A7F3D0" : "#E5E7EB"}`,
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: "50%",
        background: isActive ? "#10B981" : "#9CA3AF",
        display: "inline-block",
      }}/>
      {status}
    </span>
  );
};

const InviteStatusBadge = ({ status }) => {
  const styles = {
    pending: { bg: "#EFF6FF", color: "#1D4ED8", border: "#BFDBFE" },
    expired: { bg: "#FFFBEB", color: "#92400E", border: "#FDE68A" },
    cancelled: { bg: "#F3F4F6", color: "#6B7280", border: "#E5E7EB" },
  };
  const s = styles[status] || styles.pending;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      padding: "3px 10px", borderRadius: 20, fontSize: 11, fontWeight: 600,
      background: s.bg, color: s.color, border: `1px solid ${s.border}`,
    }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: s.color, display: "inline-block" }}/>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

function Dropdown({ trigger, children, align = "left" }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);
  return (
    <div ref={ref} style={{ position: "relative", display: "inline-block" }}>
      <div onClick={() => setOpen(v => !v)}>{trigger}</div>
      {open && (
        <div style={{
          position: "absolute", top: "calc(100% + 6px)",
          [align === "right" ? "right" : "left"]: 0,
          background: "#fff", borderRadius: 10,
          boxShadow: "0 8px 30px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06)",
          border: "1px solid #E5E7EB", minWidth: 180, zIndex: 999, overflow: "hidden",
        }}>
          <div onClick={() => setOpen(false)}>{children}</div>
        </div>
      )}
    </div>
  );
}

const DropdownItem = ({ icon, label, color, onClick }) => (
  <div onClick={onClick} style={{
    display: "flex", alignItems: "center", gap: 10, padding: "9px 14px",
    fontSize: 13, color: color || "#374151", cursor: "pointer",
    transition: "background 0.15s",
  }}
    onMouseEnter={e => e.currentTarget.style.background = "#F9FAFB"}
    onMouseLeave={e => e.currentTarget.style.background = "transparent"}
  >
    {icon && <span style={{ color: color || "#6B7280" }}>{icon}</span>}
    {label}
  </div>
);

const TH = ({ children, sortable }) => (
  <th style={{
    padding: "11px 16px", textAlign: "left", fontSize: 12.5, fontWeight: 600,
    color: "#6B7280", background: "#F9FAFB", borderBottom: "1px solid #E5E7EB",
    whiteSpace: "nowrap", userSelect: "none",
  }}>
    <span style={{ display: "inline-flex", alignItems: "center", gap: 4, cursor: sortable ? "pointer" : "default" }}>
      {children}
      {sortable && <ChevronDown size={12} />}
    </span>
  </th>
);
const TD = ({ children, style }) => (
  <td style={{ padding: "12px 16px", fontSize: 13, color: "#111827", borderBottom: "1px solid #F3F4F6", ...style }}>
    {children}
  </td>
);

// ── Modal ────────────────────────────────────────────────────────────────────
function InviteModal({ onClose }) {
  const [form, setForm] = useState({ name: "", email: "", role_id: "" });
  const roles = ["Super Admin", "Team Lead", "Sales Agent"];
  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 9999,
    }} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={{
        background: "#fff", borderRadius: 14, width: 460, padding: "28px 32px",
        boxShadow: "0 20px 60px rgba(0,0,0,0.18)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <div>
            <div style={{ fontSize: 17, fontWeight: 700, color: "#111827" }}>Invite User</div>
            <div style={{ fontSize: 12.5, color: "#9CA3AF", marginTop: 2 }}>Send an invitation email to a new staff member</div>
          </div>
          <button onClick={onClose} style={{ background: "#F3F4F6", border: "none", borderRadius: 8, width: 30, height: 30, cursor: "pointer", fontSize: 16, color: "#6B7280" }}>×</button>
        </div>
        {[
          { label: "Full Name", key: "name", type: "text", placeholder: "e.g. Jane Smith" },
          { label: "Email Address", key: "email", type: "email", placeholder: "e.g. jane@company.com" },
        ].map(f => (
          <div key={f.key} style={{ marginBottom: 16 }}>
            <label style={{ display: "block", fontSize: 12.5, fontWeight: 600, color: "#374151", marginBottom: 6 }}>{f.label} <span style={{ color: "#EF4444" }}>*</span></label>
            <input type={f.type} placeholder={f.placeholder} value={form[f.key]}
              onChange={e => setForm(v => ({ ...v, [f.key]: e.target.value }))}
              style={{ width: "100%", padding: "9px 12px", borderRadius: 8, border: "1.5px solid #E5E7EB", fontSize: 13, color: "#111827", outline: "none", boxSizing: "border-box", transition: "border-color 0.15s" }}
              onFocus={e => e.target.style.borderColor = "#0D9488"}
              onBlur={e => e.target.style.borderColor = "#E5E7EB"}
            />
          </div>
        ))}
        <div style={{ marginBottom: 24 }}>
          <label style={{ display: "block", fontSize: 12.5, fontWeight: 600, color: "#374151", marginBottom: 6 }}>Role <span style={{ color: "#EF4444" }}>*</span></label>
          <select value={form.role_id} onChange={e => setForm(v => ({ ...v, role_id: e.target.value }))}
            style={{ width: "100%", padding: "9px 12px", borderRadius: 8, border: "1.5px solid #E5E7EB", fontSize: 13, color: form.role_id ? "#111827" : "#9CA3AF", outline: "none", background: "#fff", boxSizing: "border-box" }}>
            <option value="">Select a role</option>
            {roles.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
        <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
          <button onClick={onClose} style={{ padding: "9px 20px", borderRadius: 8, border: "1.5px solid #E5E7EB", background: "#fff", fontSize: 13, fontWeight: 600, color: "#374151", cursor: "pointer" }}>Cancel</button>
          <button style={{ padding: "9px 20px", borderRadius: 8, border: "none", background: "linear-gradient(135deg, #0F766E, #0D9488)", fontSize: 13, fontWeight: 600, color: "#fff", cursor: "pointer", display: "flex", alignItems: "center", gap: 6 }}>
            <InviteIcon /> Send Invitation
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Main Component ───────────────────────────────────────────────────────────
export default function UsersStaffScreen() {
  const [view, setView] = useState("list");        // list | invitation
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [search, setSearch] = useState("");
  const [actionOpen, setActionOpen] = useState(null);
  const actionRef = useRef(null);

  useEffect(() => {
    const handler = (e) => { if (actionRef.current && !actionRef.current.contains(e.target)) setActionOpen(null); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const filteredUsers = mockUsers.filter(u =>
    !search ||
    u.display_name.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase()) ||
    u.code.toLowerCase().includes(search.toLowerCase())
  );

  const filteredInvitations = mockInvitations.filter(i =>
    !search ||
    i.name.toLowerCase().includes(search.toLowerCase()) ||
    i.email.toLowerCase().includes(search.toLowerCase())
  );

  const TEAL = "#0D9488";
  const TEAL_DARK = "#0F766E";
  const TEAL_BTN = { background: `linear-gradient(135deg, ${TEAL_DARK}, ${TEAL})`, color: "#fff", border: "none" };

  return (
    <div style={{ fontFamily: "'DM Sans', 'Segoe UI', sans-serif", background: "#F8FAFC", minHeight: "100vh", display: "flex", flexDirection: "column" }}>

      {/* ── Top Nav ── */}
      <header style={{ background: "#fff", borderBottom: "1px solid #E5E7EB", height: 54, display: "flex", alignItems: "center", padding: "0 20px", gap: 12, position: "sticky", top: 0, zIndex: 100 }}>
        <button style={{ background: "none", border: "none", cursor: "pointer", color: "#6B7280", display: "flex", alignItems: "center", padding: 4 }}><HamburgerIcon /></button>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 28, height: 28, borderRadius: 8, background: "linear-gradient(135deg,#0F766E,#0D9488)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span style={{ fontSize: 13, fontWeight: 800, color: "#fff" }}>V</span>
          </div>
          <span style={{ fontSize: 14, fontWeight: 800, color: "#0F172A", letterSpacing: "-0.3px" }}>VANGUARD X</span>
        </div>
        <div style={{ flex: 1 }} />
        {/* Breadcrumb */}
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12.5, color: "#9CA3AF" }}>
          <HomeIcon />
          <ChevronRight /><span style={{ color: "#6B7280" }}>Core</span>
          <ChevronRight /><span style={{ color: TEAL, fontWeight: 600 }}>Users/Staffs</span>
        </div>
        <div style={{ flex: 1 }} />
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <button style={{ background: "none", border: "none", cursor: "pointer", color: "#6B7280", display: "flex", position: "relative" }}>
            <BellIcon />
            <span style={{ position: "absolute", top: -2, right: -2, width: 8, height: 8, borderRadius: "50%", background: "#EF4444", border: "1.5px solid #fff" }} />
          </button>
          <button style={{ background: "none", border: "none", cursor: "pointer", color: "#6B7280", display: "flex", alignItems: "center", gap: 4, fontSize: 12.5, fontWeight: 600 }}>
            <GlobeIcon /> EN
          </button>
          <button style={{ background: "none", border: "none", cursor: "pointer", color: "#6B7280", display: "flex" }}><MoonIcon /></button>
          <div style={{ width: 30, height: 30, borderRadius: "50%", background: "linear-gradient(135deg,#0F766E,#14B8A6)", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer" }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: "#fff" }}>A</span>
          </div>
        </div>
      </header>

      <div style={{ display: "flex", flex: 1 }}>

        {/* ── Sidebar ── */}
        <aside style={{ width: 200, background: "#fff", borderRight: "1px solid #E5E7EB", padding: "16px 0", flexShrink: 0 }}>
          {[
            { label: "Dashboard", active: false },
            { label: "Core", active: true, expanded: true },
          ].map(item => (
            <div key={item.label} style={{ padding: "8px 18px", fontSize: 13, fontWeight: item.active ? 600 : 500, color: item.active ? TEAL_DARK : "#374151", display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer" }}>
              {item.label}
              {item.expanded && <ChevronDown size={13} />}
            </div>
          ))}
          {["Roles", "Accounts", "Users/Staffs", "Teams", "Contacts", "Templates", "Flags", "Channels", "Reasons"].map(item => (
            <div key={item} onClick={() => {}} style={{
              padding: "7px 18px 7px 30px", fontSize: 12.5,
              fontWeight: item === "Users/Staffs" ? 600 : 400,
              color: item === "Users/Staffs" ? TEAL : "#6B7280",
              background: item === "Users/Staffs" ? "#F0FDFA" : "transparent",
              borderRight: item === "Users/Staffs" ? `2px solid ${TEAL}` : "2px solid transparent",
              cursor: "pointer", transition: "all 0.15s",
            }}
              onMouseEnter={e => { if (item !== "Users/Staffs") { e.currentTarget.style.background = "#F9FAFB"; e.currentTarget.style.color = "#374151"; } }}
              onMouseLeave={e => { if (item !== "Users/Staffs") { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "#6B7280"; } }}
            >
              {item}
            </div>
          ))}
        </aside>

        {/* ── Main Content ── */}
        <main style={{ flex: 1, padding: "24px 28px", minWidth: 0 }}>

          {/* ── Page Header ── */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
            <h1 style={{ fontSize: 20, fontWeight: 700, color: "#0F172A", margin: 0 }}>User/Staff</h1>

            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>

              {/* List View dropdown */}
              <Dropdown
                align="left"
                trigger={
                  <button style={{ display: "flex", alignItems: "center", gap: 7, padding: "8px 14px", borderRadius: 8, ...TEAL_BTN, fontSize: 12.5, fontWeight: 600, cursor: "pointer" }}>
                    <ListIcon /> {view === "list" ? "List view" : view === "invitation" ? "Invitation List" : "List view"} <ChevronDown size={13} />
                  </button>
                }
              >
                <div style={{ padding: "6px 0" }}>
                  <DropdownItem icon={<ListIcon />} label="List view" onClick={() => setView("list")} />
                  <DropdownItem icon={<HierarchyIcon />} label="Staff Hierarchy View" onClick={() => setView("hierarchy")} />
                  <DropdownItem icon={<TeamIcon />} label="Team View" onClick={() => setView("team")} />
                </div>
              </Dropdown>

              {/* Invitation List button */}
              <button
                onClick={() => setView(view === "invitation" ? "list" : "invitation")}
                style={{
                  display: "flex", alignItems: "center", gap: 7, padding: "8px 14px", borderRadius: 8,
                  background: view === "invitation" ? "#0F766E" : TEAL, color: "#fff", border: "none",
                  fontSize: 12.5, fontWeight: 600, cursor: "pointer",
                  boxShadow: view === "invitation" ? "inset 0 2px 4px rgba(0,0,0,0.15)" : "none",
                }}
              >
                <ListIcon /> Invitation List
              </button>

              {/* Invite User */}
              <button
                onClick={() => setShowInviteModal(true)}
                style={{ display: "flex", alignItems: "center", gap: 7, padding: "8px 14px", borderRadius: 8, ...TEAL_BTN, fontSize: 12.5, fontWeight: 600, cursor: "pointer" }}
              >
                <InviteIcon /> Invite User
              </button>

              {/* Create Sales Team */}
              <button style={{ display: "flex", alignItems: "center", gap: 7, padding: "8px 14px", borderRadius: 8, ...TEAL_BTN, fontSize: 12.5, fontWeight: 600, cursor: "pointer" }}>
                <InviteIcon /> Create Sales Team
              </button>
            </div>
          </div>

          {/* ── Table Card ── */}
          <div style={{ background: "#fff", borderRadius: 12, border: "1px solid #E5E7EB", overflow: "hidden", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>

            {/* Table Toolbar */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", borderBottom: "1px solid #F3F4F6" }}>
              <div style={{ position: "relative", width: 240 }}>
                <span style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)" }}><SearchIcon /></span>
                <input
                  placeholder="Search..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  style={{ width: "100%", padding: "8px 12px 8px 32px", borderRadius: 8, border: "1.5px solid #E5E7EB", fontSize: 13, color: "#111827", outline: "none", boxSizing: "border-box" }}
                  onFocus={e => e.target.style.borderColor = TEAL}
                  onBlur={e => e.target.style.borderColor = "#E5E7EB"}
                />
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                {[<FilterIcon />, <ColumnsIcon />, <ExpandIcon />].map((icon, i) => (
                  <button key={i} style={{ background: "none", border: "1.5px solid #E5E7EB", borderRadius: 8, width: 34, height: 34, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", color: "#6B7280" }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = TEAL; e.currentTarget.style.color = TEAL; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = "#E5E7EB"; e.currentTarget.style.color = "#6B7280"; }}
                  >{icon}</button>
                ))}
              </div>
            </div>

            {/* ── Users List View ── */}
            {view === "list" && (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr>
                      <TH><input type="checkbox" style={{ accentColor: TEAL }} /></TH>
                      <TH sortable>Display Name</TH>
                      <TH sortable>Staff Code</TH>
                      <TH sortable>User Role</TH>
                      <TH sortable>Email</TH>
                      <TH sortable>Contact Number</TH>
                      <TH sortable>Status</TH>
                      <TH>Action</TH>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map(user => (
                      <tr key={user.id} style={{ transition: "background 0.1s" }}
                        onMouseEnter={e => e.currentTarget.style.background = "#FAFAFA"}
                        onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                      >
                        <TD><input type="checkbox" style={{ accentColor: TEAL }} /></TD>
                        <TD>
                          <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
                            <div style={{
                              width: 30, height: 30, borderRadius: "50%", flexShrink: 0,
                              background: `linear-gradient(135deg, ${TEAL_DARK}, #14B8A6)`,
                              display: "flex", alignItems: "center", justifyContent: "center",
                              fontSize: 11, fontWeight: 700, color: "#fff",
                            }}>
                              {user.display_name.charAt(0).toUpperCase()}
                            </div>
                            <span style={{ fontWeight: 500, color: "#111827" }}>{user.display_name}</span>
                          </div>
                        </TD>
                        <TD><span style={{ fontFamily: "monospace", fontSize: 12, background: "#F3F4F6", padding: "2px 7px", borderRadius: 5, color: "#374151" }}>{user.code}</span></TD>
                        <TD style={{ color: "#374151" }}>{user.role}</TD>
                        <TD style={{ color: "#6B7280" }}>{user.email}</TD>
                        <TD style={{ color: "#6B7280" }}>{user.contact_no || <span style={{ color: "#D1D5DB" }}>—</span>}</TD>
                        <TD><StatusBadge status={user.status} /></TD>
                        <TD>
                          <div style={{ position: "relative" }} ref={actionOpen === user.id ? actionRef : null}>
                            <button
                              onClick={() => setActionOpen(actionOpen === user.id ? null : user.id)}
                              style={{ background: "none", border: "1.5px solid #E5E7EB", borderRadius: 7, width: 30, height: 30, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", color: "#6B7280" }}
                              onMouseEnter={e => { e.currentTarget.style.borderColor = TEAL; e.currentTarget.style.color = TEAL; }}
                              onMouseLeave={e => { e.currentTarget.style.borderColor = "#E5E7EB"; e.currentTarget.style.color = "#6B7280"; }}
                            >
                              <DotsIcon />
                            </button>
                            {actionOpen === user.id && (
                              <div style={{
                                position: "absolute", right: 0, top: "calc(100% + 6px)",
                                background: "#fff", borderRadius: 10,
                                boxShadow: "0 8px 30px rgba(0,0,0,0.12)",
                                border: "1px solid #E5E7EB", minWidth: 150, zIndex: 999,
                              }}>
                                {[
                                  { label: "View", color: "#374151" },
                                  { label: "Edit", color: "#374151" },
                                  { label: user.status === "Active" ? "Deactivate" : "Reactivate", color: user.status === "Active" ? "#D97706" : "#059669" },
                                  { label: "Delete", color: "#EF4444" },
                                ].map(a => (
                                  <div key={a.label} onClick={() => setActionOpen(null)} style={{ padding: "9px 14px", fontSize: 13, color: a.color, cursor: "pointer" }}
                                    onMouseEnter={e => e.currentTarget.style.background = "#F9FAFB"}
                                    onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                                  >{a.label}</div>
                                ))}
                              </div>
                            )}
                          </div>
                        </TD>
                      </tr>
                    ))}
                    {filteredUsers.length === 0 && (
                      <tr><td colSpan={8} style={{ textAlign: "center", padding: "40px 16px", color: "#9CA3AF", fontSize: 13 }}>No users found.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* ── Invitation List View ── */}
            {view === "invitation" && (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr>
                      <TH><input type="checkbox" style={{ accentColor: TEAL }} /></TH>
                      <TH sortable>Name</TH>
                      <TH sortable>Email</TH>
                      <TH sortable>Role</TH>
                      <TH sortable>Invited By</TH>
                      <TH sortable>Invited On</TH>
                      <TH sortable>Link Expires At</TH>
                      <TH sortable>Resent</TH>
                      <TH sortable>Status</TH>
                      <TH>Action</TH>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredInvitations.map(inv => (
                      <tr key={inv.id} style={{ transition: "background 0.1s" }}
                        onMouseEnter={e => e.currentTarget.style.background = "#FAFAFA"}
                        onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                      >
                        <TD><input type="checkbox" style={{ accentColor: TEAL }} /></TD>
                        <TD>
                          <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
                            <div style={{ width: 30, height: 30, borderRadius: "50%", flexShrink: 0, background: "linear-gradient(135deg,#6366F1,#818CF8)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: "#fff" }}>
                              {inv.name.charAt(0)}
                            </div>
                            <span style={{ fontWeight: 500, color: "#111827" }}>{inv.name}</span>
                          </div>
                        </TD>
                        <TD style={{ color: "#6B7280" }}>{inv.email}</TD>
                        <TD style={{ color: "#374151" }}>{inv.role}</TD>
                        <TD style={{ color: "#6B7280" }}>{inv.invited_by}</TD>
                        <TD style={{ color: "#6B7280", fontSize: 12 }}>{inv.invited_on}</TD>
                        <TD>
                          <span style={{ color: inv.status === "expired" ? "#D97706" : "#6B7280", fontSize: 12 }}>
                            {inv.expires_at}
                          </span>
                        </TD>
                        <TD>
                          <span style={{ fontSize: 12, color: inv.resent_count > 0 ? TEAL : "#9CA3AF" }}>
                            {inv.resent_count > 0 ? inv.resent_count : "—"}
                          </span>
                        </TD>
                        <TD><InviteStatusBadge status={inv.status} /></TD>
                        <TD>
                          <div style={{ display: "flex", gap: 6 }}>
                            <button style={{ padding: "5px 11px", borderRadius: 6, border: `1.5px solid ${TEAL}`, background: "#fff", color: TEAL, fontSize: 11.5, fontWeight: 600, cursor: "pointer" }}
                              onMouseEnter={e => { e.currentTarget.style.background = TEAL; e.currentTarget.style.color = "#fff"; }}
                              onMouseLeave={e => { e.currentTarget.style.background = "#fff"; e.currentTarget.style.color = TEAL; }}
                            >Resend</button>
                            <button style={{ padding: "5px 11px", borderRadius: 6, border: "1.5px solid #FCA5A5", background: "#fff", color: "#EF4444", fontSize: 11.5, fontWeight: 600, cursor: "pointer" }}
                              onMouseEnter={e => { e.currentTarget.style.background = "#FEF2F2"; }}
                              onMouseLeave={e => { e.currentTarget.style.background = "#fff"; }}
                            >Cancel</button>
                          </div>
                        </TD>
                      </tr>
                    ))}
                    {filteredInvitations.length === 0 && (
                      <tr><td colSpan={10} style={{ textAlign: "center", padding: "40px 16px", color: "#9CA3AF", fontSize: 13 }}>No pending invitations.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* ── Hierarchy / Team placeholder ── */}
            {(view === "hierarchy" || view === "team") && (
              <div style={{ padding: "60px 40px", textAlign: "center", color: "#9CA3AF" }}>
                <div style={{ fontSize: 32, marginBottom: 12 }}>
                  {view === "hierarchy" ? "🏗️" : "👥"}
                </div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "#6B7280", marginBottom: 4 }}>
                  {view === "hierarchy" ? "Staff Hierarchy View" : "Team View"}
                </div>
                <div style={{ fontSize: 12.5 }}>This view is rendered separately based on hierarchy data.</div>
              </div>
            )}

            {/* Pagination */}
            {(view === "list" || view === "invitation") && (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", borderTop: "1px solid #F3F4F6" }}>
                <span style={{ fontSize: 12.5, color: "#9CA3AF" }}>
                  Showing {view === "list" ? filteredUsers.length : filteredInvitations.length} of {view === "list" ? mockUsers.length : mockInvitations.length} records
                </span>
                <div style={{ display: "flex", gap: 4 }}>
                  {[1, 2, 3].map(n => (
                    <button key={n} style={{ width: 30, height: 30, borderRadius: 6, border: n === 1 ? "none" : "1.5px solid #E5E7EB", background: n === 1 ? TEAL : "#fff", color: n === 1 ? "#fff" : "#6B7280", fontSize: 12.5, cursor: "pointer", fontWeight: n === 1 ? 600 : 400 }}>{n}</button>
                  ))}
                  <button style={{ padding: "0 10px", height: 30, borderRadius: 6, border: "1.5px solid #E5E7EB", background: "#fff", color: "#6B7280", fontSize: 12.5, cursor: "pointer" }}>Next →</button>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* ── Invite Modal ── */}
      {showInviteModal && <InviteModal onClose={() => setShowInviteModal(false)} />}
    </div>
  );
}

/*
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| UI Implementation | Completed | Antigravity | Refactored UsersPage to match premium design, implemented toolbar, list/invitation views, functional dropdowns, and modal overlay. |
| Verification | Completed | Antigravity | Verified code structure, styling, and backend alignment for invitation fields. |
*/
