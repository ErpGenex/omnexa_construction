# Patch to add database indexes for performance optimization

import frappe


def execute():
	"""Add database indexes for frequently queried fields"""
	
	# Indexes for Project Contract
	project_contract_indexes = [
		{
			"table": "`tabProject Contract`",
			"index_name": "idx_project_contract_title",
			"columns": ["contract_title"]
		},
		{
			"table": "`tabProject Contract`",
			"index_name": "idx_project_contract_client",
			"columns": ["client"]
		},
		{
			"table": "`tabProject Contract`",
			"index_name": "idx_project_contract_status",
			"columns": ["status"]
		}
	]
	
	# Indexes for BOQ Item
	boq_item_indexes = [
		{
			"table": "`tabBOQ Item`",
			"index_name": "idx_boq_item_project",
			"columns": ["project"]
		},
		{
			"table": "`tabBOQ Item`",
			"index_name": "idx_boq_item_item_code",
			"columns": ["item_code"]
		}
	]
	
	# Indexes for Construction CDE Document
	cde_document_indexes = [
		{
			"table": "`tabConstruction CDE Document`",
			"index_name": "idx_cde_document_project",
			"columns": ["project"]
		},
		{
			"table": "`tabConstruction CDE Document`",
			"index_name": "idx_cde_document_document_type",
			"columns": ["document_type"]
		},
		{
			"table": "`tabConstruction CDE Document`",
			"index_name": "idx_cde_document_iso19650_status",
			"columns": ["iso19650_status"]
		}
	]
	
	# Indexes for Primavera Integration Log
	primavera_log_indexes = [
		{
			"table": "`tabPrimavera Integration Log`",
			"index_name": "idx_primavera_log_entity_type",
			"columns": ["entity_type"]
		},
		{
			"table": "`tabPrimavera Integration Log`",
			"index_name": "idx_primavera_log_status",
			"columns": ["status"]
		},
		{
			"table": "`tabPrimavera Integration Log`",
			"index_name": "idx_primavera_log_sync_timestamp",
			"columns": ["sync_timestamp"]
		}
	]
	
	# Indexes for Primavera Sync Queue
	primavera_queue_indexes = [
		{
			"table": "`tabPrimavera Sync Queue`",
			"index_name": "idx_primavera_queue_status",
			"columns": ["status"]
		},
		{
			"table": "`tabPrimavera Sync Queue`",
			"index_name": "idx_primavera_queue_priority",
			"columns": ["priority"]
		},
		{
			"table": "`tabPrimavera Sync Queue`",
			"index_name": "idx_primavera_queue_next_attempt",
			"columns": ["next_attempt"]
		}
	]
	
	# Create indexes
	for index_info in project_contract_indexes + boq_item_indexes + cde_document_indexes + primavera_log_indexes + primavera_queue_indexes:
		try:
			# Check if index exists first
			index_exists = frappe.db.sql(f"""
				SELECT COUNT(*) FROM information_schema.statistics
				WHERE table_schema = DATABASE()
				AND table_name = {index_info['table'].replace('`', "'")}
				AND index_name = '{index_info['index_name']}'
			""")[0][0]
			
			if not index_exists:
				frappe.db.sql(f"""
					CREATE INDEX {index_info['index_name']}
					ON {index_info['table']} ({', '.join(index_info['columns'])})
				""")
		except Exception as e:
			frappe.log_error(f"Failed to create index {index_info['index_name']}: {str(e)}", "Performance Optimization")
	
	frappe.db.commit()
