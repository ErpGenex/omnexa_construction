// Primavera P6 Sync Buttons - Client Script
// Adds manual sync buttons to Project Contract, PM WBS Task, and Resource forms

frappe.ui.form.on('Project Contract', {
	refresh: function(frm) {
		// Add Sync to P6 button
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button('Sync to P6', function() {
				frappe.call({
					method: 'omnexa_construction.api.primavera.sync_project_to_p6',
					args: {
						project_id: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.status === 'success') {
							frappe.msgprint('Project synced to P6 successfully');
							frm.reload_doc();
						} else {
							frappe.msgprint('Sync failed: ' + (r.message.error || 'Unknown error'));
						}
					}
				});
			}, 'Primavera P6');
			
			// Add Sync from P6 button
			if (frm.doc.p6_project_id) {
				frm.add_custom_button('Sync from P6', function() {
					frappe.call({
						method: 'omnexa_construction.api.primavera.sync_project_from_p6',
						args: {
							p6_project_id: frm.doc.p6_project_id
						},
						callback: function(r) {
							if (r.message && r.message.status === 'success') {
								frappe.msgprint('Project synced from P6 successfully');
								frm.reload_doc();
							} else {
								frappe.msgprint('Sync failed: ' + (r.message.error || 'Unknown error'));
							}
						}
					});
				}, 'Primavera P6');
			}
		}
		
		// Show sync status indicator
		if (frm.doc.p6_sync_status) {
			var status_color = frm.doc.p6_sync_status === 'Synced' ? 'green' : 
				frm.doc.p6_sync_status === 'Sync Failed' ? 'red' : 'orange';
			
			frm.dashboard.add_indicator(
				'P6 Sync: ' + frm.doc.p6_sync_status,
				status_color
			);
		}
	}
});

frappe.ui.form.on('PM WBS Task', {
	refresh: function(frm) {
		// Add Sync to P6 button
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button('Sync to P6', function() {
				frappe.call({
					method: 'omnexa_construction.api.primavera.sync_task_to_p6',
					args: {
						task_id: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.status === 'success') {
							frappe.msgprint('Task synced to P6 successfully');
							frm.reload_doc();
						} else {
							frappe.msgprint('Sync failed: ' + (r.message.error || 'Unknown error'));
						}
					}
				});
			}, 'Primavera P6');
		}
		
		// Show sync status indicator
		if (frm.doc.p6_sync_status) {
			var status_color = frm.doc.p6_sync_status === 'Synced' ? 'green' : 
				frm.doc.p6_sync_status === 'Sync Failed' ? 'red' : 'orange';
			
			frm.dashboard.add_indicator(
				'P6 Sync: ' + frm.doc.p6_sync_status,
				status_color
			);
		}
	}
});

frappe.ui.form.on('Resource', {
	refresh: function(frm) {
		// Add Sync to P6 button
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button('Sync to P6', function() {
				frappe.call({
					method: 'omnexa_construction.api.primavera.sync_resource_to_p6',
					args: {
						resource_id: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.status === 'success') {
							frappe.msgprint('Resource synced to P6 successfully');
							frm.reload_doc();
						} else {
							frappe.msgprint('Sync failed: ' + (r.message.error || 'Unknown error'));
						}
					}
				});
			}, 'Primavera P6');
		}
		
		// Show sync status indicator
		if (frm.doc.p6_sync_status) {
			var status_color = frm.doc.p6_sync_status === 'Synced' ? 'green' : 
				frm.doc.p6_sync_status === 'Sync Failed' ? 'red' : 'orange';
			
			frm.dashboard.add_indicator(
				'P6 Sync: ' + frm.doc.p6_sync_status,
				status_color
			);
		}
	}
});
