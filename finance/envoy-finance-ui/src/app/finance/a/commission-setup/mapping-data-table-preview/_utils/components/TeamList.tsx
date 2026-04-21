import React from 'react';

type User = {
  id: string;
  name: string;
};

type TeamListProps = {
  accountManagers: User[];
  teamMembers: User[];
  onRemove: (id: string, isManager: boolean) => void;
};

const TeamList: React.FC<TeamListProps> = ({ accountManagers, teamMembers, onRemove }) => {
  const renderUserCard = (user: User, isManager = false) => (
    <div key={user.id} className="d-flex align-items-center justify-content-between mb-3">
      <div className="d-flex align-items-center">
        <img src="https://via.placeholder.com/40" alt="Profile" className="rounded-circle me-2" style={{ width: '40px', height: '40px' }} />
        <div>
          <div className="fw-semibold">{user.name}</div>
          <div className="text-muted small">#{user.id}</div>
        </div>
      </div>
      <button
        className="btn btn-sm btn-light border rounded-circle"
        onClick={() => onRemove(user.id, isManager)}
        style={{ width: '28px', height: '28px', fontWeight: 'bold', lineHeight: '0' }}
        aria-label="Remove"
      >
        ×
      </button>
    </div>
  );

  return (
    <div className="row">
      {/* Account Manager Column */}
      <div className="col-md-6 p-3">
        <div className="card shadow-sm p-3" style={{ borderRadius: '12px' }}>
          <h6 className="mb-3" style={{ color: '#344054' }}>
            Account Manager
          </h6>
          {accountManagers.length > 0 ? accountManagers.map((manager) => renderUserCard(manager, true)) : <p className="text-muted">No account managers.</p>}
          <button className="btn btn-outline-primary btn-sm mt-2">
            <span className="me-1">+</span> Add New
          </button>
        </div>
      </div>

      {/* Sales Team Column */}
      <div className="col-md-6 p-3">
        <div className="card shadow-sm p-3" style={{ borderRadius: '12px' }}>
          <h6 className="mb-3" style={{ color: '#344054' }}>
            Sales Team
          </h6>
          {teamMembers.length > 0 ? teamMembers.map((member) => renderUserCard(member)) : <p className="text-muted">No sales team members.</p>}
        </div>
      </div>
    </div>
  );
};

export default TeamList;
