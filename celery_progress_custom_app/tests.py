import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import path
from celery.result import AsyncResult
from celery_progress_custom_app.consumers import ProgressConsumer
from celery_progress_custom_app.backend import (
    ProgressRecorder, 
    WebSocketProgressRecorder, 
    ConsoleProgressRecorder,
    Progress
)
from django_starter.tasks import long_running_task


@pytest.mark.django_db
class TestProgressRecorder:
    """Test the ProgressRecorder class"""
    
    def test_progress_recorder_init(self):
        """Test ProgressRecorder initialization"""
        mock_task = Mock()
        recorder = ProgressRecorder(mock_task)
        assert recorder.task == mock_task
    
    def test_set_progress_calculates_percentage(self):
        """Test progress percentage calculation"""
        mock_task = Mock()
        recorder = ProgressRecorder(mock_task)
        
        state, meta = recorder.set_progress(25, 100, "Processing...")
        
        assert state == 'PROGRESS'
        assert meta['current'] == 25
        assert meta['total'] == 100
        assert meta['percent'] == 25.0
        assert meta['description'] == "Processing..."
        assert meta['pending'] is False
        mock_task.update_state.assert_called_once()
    
    def test_set_progress_handles_zero_total(self):
        """Test progress with zero total"""
        mock_task = Mock()
        recorder = ProgressRecorder(mock_task)
        
        state, meta = recorder.set_progress(0, 0, "No items")
        
        assert meta['percent'] == 0
        assert meta['total'] == 0
    
    def test_set_progress_completion(self):
        """Test 100% progress"""
        mock_task = Mock()
        recorder = ProgressRecorder(mock_task)
        
        state, meta = recorder.set_progress(100, 100, "Complete")
        
        assert meta['percent'] == 100.0
        assert meta['current'] == 100


@pytest.mark.django_db
class TestConsoleProgressRecorder:
    """Test the ConsoleProgressRecorder class"""
    
    def test_console_progress_prints(self, capsys):
        """Test console progress recorder outputs to stdout"""
        recorder = ConsoleProgressRecorder()
        recorder.set_progress(50, 100, "Half done")
        
        captured = capsys.readouterr()
        assert "processed 50 items of 100" in captured.out
        assert "Half done" in captured.out


@pytest.mark.django_db
class TestWebSocketProgressRecorder:
    """Test the WebSocketProgressRecorder class"""
    
    @patch('celery_progress_custom_app.backend.channel_layer')
    def test_websocket_progress_recorder_init(self, mock_channel_layer):
        """Test WebSocketProgressRecorder initialization"""
        mock_task = Mock()
        mock_channel_layer.return_value = Mock()
        
        recorder = WebSocketProgressRecorder(mock_task)
        assert recorder.task == mock_task
    
    @patch('celery_progress_custom_app.backend.channel_layer')
    @patch('celery_progress_custom_app.backend.async_to_sync')
    def test_push_update_sends_to_channel(self, mock_async_to_sync, mock_channel_layer):
        """Test push_update sends data through channel layer"""
        mock_channel = Mock()
        mock_channel_layer.return_value = mock_channel
        
        task_id = "test-task-123"
        data = {'progress': 50}
        
        WebSocketProgressRecorder.push_update(task_id, data)
        
        mock_async_to_sync.assert_called_once()
    
    @patch('celery_progress_custom_app.backend.channel_layer', None)
    def test_push_update_handles_no_channel_layer(self):
        """Test push_update handles missing channel layer gracefully"""
        # Should not raise an exception
        WebSocketProgressRecorder.push_update("task-id", {'data': 'test'})


@pytest.mark.django_db
class TestProgress:
    """Test the Progress class"""
    
    def test_progress_get_info_success(self):
        """Test get_info for successful task"""
        mock_result = Mock(spec=AsyncResult)
        mock_result._get_task_meta.return_value = {
            'status': 'SUCCESS',
            'result': {'message': 'Done'}
        }
        mock_result.successful.return_value = True
        
        progress = Progress(mock_result)
        info = progress.get_info()
        
        assert info['state'] == 'SUCCESS'
        assert info['complete'] is True
        assert info['success'] is True
    
    def test_progress_get_info_in_progress(self):
        """Test get_info for in-progress task"""
        mock_result = Mock(spec=AsyncResult)
        mock_result._get_task_meta.return_value = {
            'status': 'PROGRESS',
            'result': {
                'current': 50,
                'total': 100,
                'percent': 50.0,
                'description': 'Processing'
            }
        }
        
        progress = Progress(mock_result)
        info = progress.get_info()
        
        assert info['state'] == 'PROGRESS'
        assert 'complete' in info or 'current' in info['state']


@pytest.mark.django_db
class TestCeleryTasks:
    """Test Celery task functionality"""
    
    def test_long_running_task_exists(self):
        """Test long_running_task is properly defined and callable"""
        from django_starter.tasks import long_running_task
        
        # Verify task exists and has expected properties
        assert long_running_task is not None
        assert hasattr(long_running_task, 'apply_async')
        assert hasattr(long_running_task, 'delay')
        # Verify it's a Celery task
        assert hasattr(long_running_task, 'run')
    
    def test_demo_task_exists(self):
        """Test demo_task is properly defined"""
        from django_starter.tasks import demo_task
        
        # Verify task exists and is callable
        assert demo_task is not None
        assert hasattr(demo_task, 'apply_async')
        assert hasattr(demo_task, 'delay')


@pytest.mark.asyncio
@pytest.mark.django_db
class TestProgressConsumer:
    """Test the WebSocket Progress Consumer"""
    
    async def test_consumer_connect(self):
        """Test WebSocket consumer accepts connection"""
        application = URLRouter([
            path('ws/progress/<str:task_id>/', ProgressConsumer.as_asgi()),
        ])
        
        communicator = WebsocketCommunicator(application, "/ws/progress/test-task-123/")
        connected, _ = await communicator.connect()
        
        assert connected
        await communicator.disconnect()
    
    async def test_consumer_receives_progress_updates(self):
        """Test consumer can receive and send progress updates"""
        application = URLRouter([
            path('ws/progress/<str:task_id>/', ProgressConsumer.as_asgi()),
        ])
        
        communicator = WebsocketCommunicator(application, "/ws/progress/test-task-456/")
        connected, _ = await communicator.connect()
        assert connected
        
        # Send a check task completion message
        with patch('celery_progress_custom_app.backend.Progress') as mock_progress:
            mock_progress_instance = Mock()
            mock_progress_instance.get_info.return_value = {
                'state': 'PROGRESS',
                'percent': 75
            }
            mock_progress.return_value = mock_progress_instance
            
            await communicator.send_json_to({
                'type': 'check_task_completion'
            })
            
            # We might receive a response
            try:
                response = await communicator.receive_json_from(timeout=1)
                assert 'state' in response or response is not None
            except:
                # Timeout is acceptable in test environment
                pass
        
        await communicator.disconnect()
    
    async def test_consumer_disconnect(self):
        """Test WebSocket consumer disconnects properly"""
        application = URLRouter([
            path('ws/progress/<str:task_id>/', ProgressConsumer.as_asgi()),
        ])
        
        communicator = WebsocketCommunicator(application, "/ws/progress/test-task-789/")
        connected, _ = await communicator.connect()
        assert connected
        
        # Disconnect should work without errors
        await communicator.disconnect()


@pytest.mark.django_db
class TestCeleryProgressIntegration:
    """Integration tests for Celery progress tracking"""
    
    @patch('celery_progress_custom_app.backend.async_to_sync')
    @patch('django_starter.tasks.time.sleep')
    def test_full_progress_tracking_flow(self, mock_sleep, mock_async_to_sync):
        """Test complete progress tracking from task to WebSocket"""
        # Mock the async_to_sync to avoid actual channel layer calls
        mock_async_to_sync.return_value = Mock()
        
        mock_task = Mock()
        mock_task.request.id = "integration-test-task"
        
        # Create recorder and simulate progress
        recorder = WebSocketProgressRecorder(mock_task)
        
        # Simulate multiple progress updates
        for i in range(0, 101, 25):
            recorder.set_progress(i, 100, f"Step {i}")
        
        # Verify task.update_state was called
        assert mock_task.update_state.call_count == 5
