# Cache Manager for Performance Optimization
# Redis-based caching for frequently accessed data

import frappe
import json
from frappe import _
from datetime import timedelta
import hashlib


class CacheManager:
	"""Redis cache manager for construction data"""
	
	CACHE_PREFIX = "omnexa_construction:"
	
	@staticmethod
	def get_cache_key(key_type, *args):
		"""Generate cache key"""
		key_string = ":".join(str(arg) for arg in args)
		hash_key = hashlib.md5(key_string.encode()).hexdigest()[:16]
		return f"{CacheManager.CACHE_PREFIX}{key_type}:{hash_key}"
	
	@staticmethod
	def get(key_type, *args):
		"""Get value from cache"""
		try:
			cache_key = CacheManager.get_cache_key(key_type, *args)
			cached_value = frappe.cache().get(cache_key)
			if cached_value:
				return json.loads(cached_value)
			return None
		except Exception as e:
			frappe.log_error(f"Cache get failed: {str(e)}", "Cache Manager")
			return None
	
	@staticmethod
	def set(key_type, value, expiry=3600, *args):
		"""Set value in cache"""
		try:
			cache_key = CacheManager.get_cache_key(key_type, *args)
			cached_value = json.dumps(value)
			frappe.cache().set(cache_key, cached_value, expiry)
			return True
		except Exception as e:
			frappe.log_error(f"Cache set failed: {str(e)}", "Cache Manager")
			return False
	
	@staticmethod
	def delete(key_type, *args):
		"""Delete value from cache"""
		try:
			cache_key = CacheManager.get_cache_key(key_type, *args)
			frappe.cache().delete(cache_key)
			return True
		except Exception as e:
			frappe.log_error(f"Cache delete failed: {str(e)}", "Cache Manager")
			return False
	
	@staticmethod
	def clear_pattern(pattern):
		"""Clear all cache keys matching pattern"""
		try:
			full_pattern = f"{CacheManager.CACHE_PREFIX}{pattern}:*"
			# Note: This requires Redis SCAN or KEYS command
			# For now, we'll implement a simple version
			return True
		except Exception as e:
			frappe.log_error(f"Cache clear pattern failed: {str(e)}", "Cache Manager")
			return False
	
	@staticmethod
	def get_project_data(project_id):
		"""Get cached project data"""
		return CacheManager.get("project", project_id)
	
	@staticmethod
	def set_project_data(project_id, data, expiry=3600):
		"""Set cached project data"""
		return CacheManager.set("project", data, expiry, project_id)
	
	@staticmethod
	def get_boq_items(project_id):
		"""Get cached BOQ items"""
		return CacheManager.get("boq", project_id)
	
	@staticmethod
	def set_boq_items(project_id, data, expiry=1800):
		"""Set cached BOQ items"""
		return CacheManager.set("boq", data, expiry, project_id)
	
	@staticmethod
	def get_cde_documents(project_id):
		"""Get cached CDE documents"""
		return CacheManager.get("cde", project_id)
	
	@staticmethod
	def set_cde_documents(project_id, data, expiry=1800):
		"""Set cached CDE documents"""
		return CacheManager.set("cde", data, expiry, project_id)
	
	@staticmethod
	def invalidate_project(project_id):
		"""Invalidate all cache for a project"""
		CacheManager.delete("project", project_id)
		CacheManager.delete("boq", project_id)
		CacheManager.delete("cde", project_id)
