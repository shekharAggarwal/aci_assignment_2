"""Forward-chaining check of the Question 2 knowledge base (stratified negation as failure, closed world)."""
F = [
 ("Release","R1"),("Release","R2"),("Release","R3"),("Release","R4"),("Release","R5"),
 ("Author","R1","D1"),("ReviewedBy","R1","D2"),("TestsPassed","R1"),("QASignedOff","R1"),
 ("RollbackPlan","R1"),("ClientUATApproved","R1"),("CABApproved","R1"),("ForClient","R1","ClientA"),
 ("Author","R2","D2"),("ReviewedBy","R2","D3"),("TestsPassed","R2"),("QASignedOff","R2"),
 ("RollbackPlan","R2"),("ClientUATApproved","R2"),("CABApproved","R2"),("CriticalVulnerability","R2"),("ForClient","R2","ClientB"),
 ("Author","R3","D3"),("ReviewedBy","R3","D1"),("TestsPassed","R3"),("RollbackPlan","R3"),("Emergency","R3"),
 ("FixesIncident","R3","INC7"),("Severity1","INC7"),("ApprovedBy","R3","DM1"),("DeliveryManager","DM1"),
 ("InFreezeWindow","R3"),("ForClient","R3","ClientA"),
 ("Author","R4","D1"),("ReviewedBy","R4","D3"),("TestsPassed","R4"),("QASignedOff","R4"),("SchemaChange","R4"),
 ("RollbackPlan","R4"),("ClientUATApproved","R4"),("CABApproved","R4"),("ForClient","R4","ClientB"),
 ("Author","R5","D2"),("ReviewedBy","R5","D2"),("TestsPassed","R5"),("QASignedOff","R5"),
 ("RollbackPlan","R5"),("ClientUATApproved","R5"),("CABApproved","R5"),("ForClient","R5","ClientB"),
]
kb=set(F)
def has(*a): return tuple(a) in kb
def args(p): return [t[1:] for t in kb if t[0]==p]
rels=[a[0] for a in args("Release")]
def strata():
    changed=True
    while changed:  # stratum 1: positive rules + NAF only on base predicates
        changed=False; new=set()
        for r,a in args("Author"):
            if any(rr==r and p!=a for rr,p in args("ReviewedBy")): new.add(("PeerReviewed",r))   # IR1
        for r in rels:
            if has("PeerReviewed",r) and has("TestsPassed",r) and has("QASignedOff",r): new.add(("QualityCleared",r))  # IR2
            if not has("SchemaChange",r): new.add(("DataSafe",r))   # IR3 (NAF on base predicate)
            if has("SchemaChange",r) and has("DBAReviewed",r): new.add(("DataSafe",r))  # IR4
            if has("CriticalVulnerability",r): new.add(("Blocked",r))  # IR5
            if all(has(p,r) for p in ("QualityCleared","DataSafe","RollbackPlan","ClientUATApproved","CABApproved")): new.add(("Approved",r))  # IR6
            if has("Emergency",r) and any(rr==r and has("Severity1",i) for rr,i in args("FixesIncident")): new.add(("ValidEmergency",r))  # IR7
            if has("ValidEmergency",r) and has("PeerReviewed",r) and has("TestsPassed",r) and has("RollbackPlan",r) \
               and any(rr==r and has("DeliveryManager",m) for rr,m in args("ApprovedBy")): new.add(("Approved",r))  # IR8
        if not new<=kb: kb.update(new); changed=True
    for r in rels:   # stratum 2: NAF on ValidEmergency
        if has("InFreezeWindow",r) and not has("ValidEmergency",r): kb.add(("Blocked",r))  # IR9
    for r in rels:   # stratum 3: NAF on Blocked
        if has("Approved",r) and not has("Blocked",r): kb.add(("CanDeploy",r))  # IR10
    for r in rels:
        if has("CanDeploy",r) and has("ValidEmergency",r): kb.add(("RequiresPostIncidentReview",r))  # IR11
        for rr,c in args("ForClient"):
            if rr==r and has("CanDeploy",r): kb.add(("MustNotify",c,r))  # IR12
strata()
print("facts:",len(F))
for p in ("PeerReviewed","QualityCleared","DataSafe","Approved","ValidEmergency","Blocked","CanDeploy","RequiresPostIncidentReview","MustNotify"):
    print(f"{p:28}", sorted(t[1:] for t in kb if t[0]==p))
