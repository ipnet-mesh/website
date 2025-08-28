// Supabase real-time client for IPNet website
let supabaseClient = null;
let nodesSubscription = null;
let membersSubscription = null;

// Initialize Supabase client
function initSupabaseClient(supabaseConfig) {
    if (!supabaseConfig.url || !supabaseConfig.anon_key) {
        console.warn('Supabase configuration missing, real-time updates disabled');
        return false;
    }

    try {
        const { createClient } = supabase;
        supabaseClient = createClient(supabaseConfig.url, supabaseConfig.anon_key);
        console.log('Supabase client initialized successfully');
        return true;
    } catch (error) {
        console.error('Failed to initialize Supabase client:', error);
        return false;
    }
}

// Subscribe to nodes table changes
function subscribeToNodes() {
    if (!supabaseClient) return;

    nodesSubscription = supabaseClient
        .channel('nodes-changes')
        .on('postgres_changes', {
            event: '*',
            schema: 'public',
            table: 'nodes',
            filter: 'is_public=eq.true'
        }, (payload) => {
            console.log('Node data changed:', payload);
            handleNodeUpdate(payload);
        })
        .subscribe((status) => {
            console.log('Nodes subscription status:', status);
        });
}

// Subscribe to members table changes
function subscribeToMembers() {
    if (!supabaseClient) return;

    membersSubscription = supabaseClient
        .channel('members-changes')
        .on('postgres_changes', {
            event: '*',
            schema: 'public',
            table: 'members',
            filter: 'is_public=eq.true'
        }, (payload) => {
            console.log('Member data changed:', payload);
            handleMemberUpdate(payload);
        })
        .subscribe((status) => {
            console.log('Members subscription status:', status);
        });
}

// Handle node updates
function handleNodeUpdate(payload) {
    const { eventType, new: newRecord, old: oldRecord } = payload;

    switch (eventType) {
        case 'INSERT':
            handleNodeInsert(newRecord);
            break;
        case 'UPDATE':
            handleNodeChange(newRecord, oldRecord);
            break;
        case 'DELETE':
            handleNodeDelete(oldRecord);
            break;
    }
}

// Handle member updates
function handleMemberUpdate(payload) {
    const { eventType, new: newRecord, old: oldRecord } = payload;

    switch (eventType) {
        case 'INSERT':
            handleMemberInsert(newRecord);
            break;
        case 'UPDATE':
            handleMemberChange(newRecord, oldRecord);
            break;
        case 'DELETE':
            handleMemberDelete(oldRecord);
            break;
    }
}

// Use raw database node record (no transformation needed)
function transformNodeRecord(dbNode) {
    return dbNode;
}

// Use raw database member record (no transformation needed)
function transformMemberRecord(dbMember) {
    return dbMember;
}

// Handle node insertion
function handleNodeInsert(dbNode) {
    const node = transformNodeRecord(dbNode);

    // Update local nodes array if it exists
    if (window.nodes && Array.isArray(window.nodes)) {
        window.nodes.push(node);
    }

    // Trigger map update if nodes page is active
    if (window.nodesPageInstance && window.nodesPageInstance.updateMapMarkers) {
        window.nodesPageInstance.nodes.push(node);
        window.nodesPageInstance.applyFilters();
    }

    // Emit custom event
    document.dispatchEvent(new CustomEvent('nodeInserted', { detail: node }));
}

// Handle node changes (especially status updates)
function handleNodeChange(newDbNode, oldDbNode) {
    const newNode = transformNodeRecord(newDbNode);
    const oldNode = transformNodeRecord(oldDbNode);

    // Update local nodes array
    if (window.nodes && Array.isArray(window.nodes)) {
        const index = window.nodes.findIndex(n => n.node_id === newNode.node_id);
        if (index !== -1) {
            window.nodes[index] = newNode;
        }
    }

    // Update nodes page instance
    if (window.nodesPageInstance && window.nodesPageInstance.nodes) {
        const index = window.nodesPageInstance.nodes.findIndex(n => n.node_id === newNode.node_id);
        if (index !== -1) {
            window.nodesPageInstance.nodes[index] = newNode;
            window.nodesPageInstance.applyFilters();
        }
    }

    // Special handling for online status changes
    if (oldNode.is_online !== newNode.is_online) {
        console.log(`Node ${newNode.name} is now ${newNode.is_online ? 'online' : 'offline'}`);

        // Update map markers if available
        if (window.nodesPageInstance && window.nodesPageInstance.updateMapMarkers) {
            window.nodesPageInstance.updateMapMarkers();
        }
    }

    // Emit custom event
    document.dispatchEvent(new CustomEvent('nodeUpdated', {
        detail: { newNode, oldNode, changes: getChangedFields(oldNode, newNode) }
    }));
}

// Handle node deletion
function handleNodeDelete(dbNode) {
    const node = transformNodeRecord(dbNode);

    // Remove from local nodes array
    if (window.nodes && Array.isArray(window.nodes)) {
        window.nodes = window.nodes.filter(n => n.node_id !== node.node_id);
    }

    // Remove from nodes page instance
    if (window.nodesPageInstance && window.nodesPageInstance.nodes) {
        window.nodesPageInstance.nodes = window.nodesPageInstance.nodes.filter(n => n.node_id !== node.node_id);
        window.nodesPageInstance.applyFilters();
    }

    // Emit custom event
    document.dispatchEvent(new CustomEvent('nodeDeleted', { detail: node }));
}

// Handle member insertion
function handleMemberInsert(dbMember) {
    const member = transformMemberRecord(dbMember);

    // Update local members array if it exists
    if (window.members && Array.isArray(window.members)) {
        window.members.push(member);
    }

    // Emit custom event
    document.dispatchEvent(new CustomEvent('memberInserted', { detail: member }));
}

// Handle member changes
function handleMemberChange(newDbMember, oldDbMember) {
    const newMember = transformMemberRecord(newDbMember);
    const oldMember = transformMemberRecord(oldDbMember);

    // Update local members array
    if (window.members && Array.isArray(window.members)) {
        const index = window.members.findIndex(m => m.member_id === newMember.member_id);
        if (index !== -1) {
            window.members[index] = newMember;
        }
    }

    // Emit custom event
    document.dispatchEvent(new CustomEvent('memberUpdated', {
        detail: { newMember, oldMember, changes: getChangedFields(oldMember, newMember) }
    }));
}

// Handle member deletion
function handleMemberDelete(dbMember) {
    const member = transformMemberRecord(dbMember);

    // Remove from local members array
    if (window.members && Array.isArray(window.members)) {
        window.members = window.members.filter(m => m.member_id !== member.member_id);
    }

    // Emit custom event
    document.dispatchEvent(new CustomEvent('memberDeleted', { detail: member }));
}

// Get changed fields between two objects
function getChangedFields(oldObj, newObj) {
    const changes = {};
    for (const key in newObj) {
        if (oldObj[key] !== newObj[key]) {
            changes[key] = { old: oldObj[key], new: newObj[key] };
        }
    }
    return changes;
}

// Unsubscribe from all subscriptions
function unsubscribeAll() {
    if (nodesSubscription) {
        supabaseClient.removeChannel(nodesSubscription);
        nodesSubscription = null;
    }

    if (membersSubscription) {
        supabaseClient.removeChannel(membersSubscription);
        membersSubscription = null;
    }
}

// Initialize real-time subscriptions
function initSupabaseRealtime(supabaseConfig) {
    if (initSupabaseClient(supabaseConfig)) {
        subscribeToNodes();
        subscribeToMembers();

        // Cleanup on page unload
        window.addEventListener('beforeunload', unsubscribeAll);

        console.log('Supabase real-time subscriptions initialized');
        return true;
    }
    return false;
}

// Export functions for global access
window.SupabaseRealtime = {
    init: initSupabaseRealtime,
    subscribeToNodes,
    subscribeToMembers,
    unsubscribeAll
};
