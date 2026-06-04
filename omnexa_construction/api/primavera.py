# Primavera P6 REST API Endpoints
# API endpoints for Primavera P6 integration

import frappe
from frappe import _
from frappe.utils import response
import json
from omnexa_construction.integrations.primavera_p6 import get_p6_client, PrimaveraP6Sync


@frappe.whitelist()
def sync_project_to_p6(project_id):
    """
    Sync Omnexa project to Primavera P6
    
    Args:
        project_id: Omnexa Project Contract ID
        
    Returns:
        Dict with sync status
    """
    try:
        p6_client = get_p6_client()
        sync_manager = PrimaveraP6Sync(p6_client)
        result = sync_manager.sync_project_to_p6(project_id)
        return result
    except Exception as e:
        frappe.log_error(f"API sync_project_to_p6 failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}


@frappe.whitelist()
def sync_project_from_p6(p6_project_id):
    """
    Sync Primavera P6 project to Omnexa
    
    Args:
        p6_project_id: P6 Project ID
        
    Returns:
        Dict with sync status
    """
    try:
        p6_client = get_p6_client()
        sync_manager = PrimaveraP6Sync(p6_client)
        result = sync_manager.sync_project_from_p6(p6_project_id)
        return result
    except Exception as e:
        frappe.log_error(f"API sync_project_from_p6 failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}


@frappe.whitelist()
def sync_task_to_p6(task_id):
    """
    Sync Omnexa task to Primavera P6
    
    Args:
        task_id: Omnexa PM WBS Task ID
        
    Returns:
        Dict with sync status
    """
    try:
        p6_client = get_p6_client()
        sync_manager = PrimaveraP6Sync(p6_client)
        result = sync_manager.sync_task_to_p6(task_id)
        return result
    except Exception as e:
        frappe.log_error(f"API sync_task_to_p6 failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}


@frappe.whitelist()
def sync_resource_to_p6(resource_id):
    """
    Sync Omnexa resource to Primavera P6
    
    Args:
        resource_id: Omnexa Resource ID
        
    Returns:
        Dict with sync status
    """
    try:
        p6_client = get_p6_client()
        sync_manager = PrimaveraP6Sync(p6_client)
        result = sync_manager.sync_resource_to_p6(resource_id)
        return result
    except Exception as e:
        frappe.log_error(f"API sync_resource_to_p6 failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}


@frappe.whitelist()
def get_p6_projects():
    """
    Get all projects from Primavera P6
    
    Returns:
        List of P6 projects
    """
    try:
        p6_client = get_p6_client()
        projects = p6_client.get_projects()
        return {'status': 'success', 'projects': projects}
    except Exception as e:
        frappe.log_error(f"API get_p6_projects failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}


@frappe.whitelist()
def get_p6_activities(project_id):
    """
    Get all activities for a project from Primavera P6
    
    Args:
        project_id: P6 Project ID
        
    Returns:
        List of P6 activities
    """
    try:
        p6_client = get_p6_client()
        activities = p6_client.get_activities(project_id)
        return {'status': 'success', 'activities': activities}
    except Exception as e:
        frappe.log_error(f"API get_p6_activities failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}


@frappe.whitelist()
def get_p6_resources():
    """
    Get all resources from Primavera P6
    
    Returns:
        List of P6 resources
    """
    try:
        p6_client = get_p6_client()
        resources = p6_client.get_resources()
        return {'status': 'success', 'resources': resources}
    except Exception as e:
        frappe.log_error(f"API get_p6_resources failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}


@frappe.whitelist()
def test_connection():
    """
    Test connection to Primavera P6
    
    Returns:
        Dict with connection status
    """
    try:
        p6_client = get_p6_client()
        # Try to get projects as a simple test
        projects = p6_client.get_projects()
        return {
            'status': 'success',
            'message': 'Connection successful',
            'projects_count': len(projects)
        }
    except Exception as e:
        frappe.log_error(f"API test_connection failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}


@frappe.whitelist()
def get_sync_logs(entity_type=None, entity_id=None, limit=50):
    """
    Get sync logs from Primavera Integration Log
    
    Args:
        entity_type: Filter by entity type (project, task, resource)
        entity_id: Filter by entity ID
        limit: Maximum number of logs to return
        
    Returns:
        List of sync logs
    """
    try:
        filters = {}
        if entity_type:
            filters['entity_type'] = entity_type
        if entity_id:
            filters['entity_id'] = entity_id
        
        logs = frappe.get_all(
            'Primavera Integration Log',
            filters=filters,
            fields=['name', 'entity_type', 'entity_id', 'action', 'status', 
                   'error_message', 'sync_timestamp'],
            order_by='sync_timestamp desc',
            limit=limit
        )
        
        return {'status': 'success', 'logs': logs}
    except Exception as e:
        frappe.log_error(f"API get_sync_logs failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}


@frappe.whitelist()
def trigger_manual_sync(entity_type, entity_id):
    """
    Trigger manual sync for an entity
    
    Args:
        entity_type: Type of entity (project, task, resource)
        entity_id: ID of the entity
        
    Returns:
        Dict with sync status
    """
    try:
        if entity_type == 'project':
            result = sync_project_to_p6(entity_id)
        elif entity_type == 'task':
            result = sync_task_to_p6(entity_id)
        elif entity_type == 'resource':
            result = sync_resource_to_p6(entity_id)
        else:
            return {'status': 'failed', 'error': 'Invalid entity type'}
        
        return result
    except Exception as e:
        frappe.log_error(f"API trigger_manual_sync failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}


@frappe.whitelist()
def get_sync_status():
    """
    Get overall sync status
    
    Returns:
        Dict with sync statistics
    """
    try:
        # Get sync statistics
        total_logs = frappe.db.count('Primavera Integration Log')
        successful_syncs = frappe.db.count('Primavera Integration Log', {'status': 'success'})
        failed_syncs = frappe.db.count('Primavera Integration Log', {'status': 'failed'})
        
        # Get recent syncs
        recent_logs = frappe.get_all(
            'Primavera Integration Log',
            fields=['entity_type', 'entity_id', 'action', 'status', 'sync_timestamp'],
            order_by='sync_timestamp desc',
            limit=10
        )
        
        return {
            'status': 'success',
            'statistics': {
                'total_syncs': total_logs,
                'successful_syncs': successful_syncs,
                'failed_syncs': failed_syncs,
                'success_rate': (successful_syncs / total_logs * 100) if total_logs > 0 else 0
            },
            'recent_syncs': recent_logs
        }
    except Exception as e:
        frappe.log_error(f"API get_sync_status failed: {str(e)}", "Primavera P6 API")
        return {'status': 'failed', 'error': str(e)}
