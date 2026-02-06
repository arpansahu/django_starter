from django.test import TestCase
from django.template import Context, Template
from custom_tag_app.templatetags.custom_tags import calculate_percentage


class CalculatePercentageFilterTestCase(TestCase):
    """Test the calculate_percentage template filter"""
    
    def test_calculate_percentage_basic(self):
        """Test basic percentage calculation"""
        result = calculate_percentage(100, 50)
        self.assertEqual(result, 50.0)
    
    def test_calculate_percentage_full(self):
        """Test 100% calculation"""
        result = calculate_percentage(100, 100)
        self.assertEqual(result, 100.0)
    
    def test_calculate_percentage_zero_read(self):
        """Test 0% calculation"""
        result = calculate_percentage(100, 0)
        self.assertEqual(result, 0.0)
    
    def test_calculate_percentage_partial(self):
        """Test partial percentage calculation"""
        result = calculate_percentage(200, 75)
        self.assertEqual(result, 37.5)
    
    def test_calculate_percentage_decimal_result(self):
        """Test decimal result"""
        result = calculate_percentage(3, 1)
        self.assertAlmostEqual(result, 33.333333333333336, places=2)
    
    def test_calculate_percentage_large_numbers(self):
        """Test with large numbers"""
        result = calculate_percentage(10000, 2500)
        self.assertEqual(result, 25.0)
    
    def test_calculate_percentage_in_template(self):
        """Test filter usage in template"""
        template = Template(
            '{% load custom_tags %}'
            '{{ pages|calculate_percentage:read }}'
        )
        
        context = Context({'pages': 100, 'read': 75})
        rendered = template.render(context)
        
        self.assertEqual(rendered.strip(), '75.0')
    
    def test_calculate_percentage_in_template_zero(self):
        """Test filter with zero in template"""
        template = Template(
            '{% load custom_tags %}'
            '{{ pages|calculate_percentage:read }}'
        )
        
        context = Context({'pages': 100, 'read': 0})
        rendered = template.render(context)
        
        self.assertEqual(rendered.strip(), '0.0')
    
    def test_calculate_percentage_in_template_full(self):
        """Test filter with 100% in template"""
        template = Template(
            '{% load custom_tags %}'
            '{{ pages|calculate_percentage:read }}'
        )
        
        context = Context({'pages': 50, 'read': 50})
        rendered = template.render(context)
        
        self.assertEqual(rendered.strip(), '100.0')


class CustomTagsIntegrationTestCase(TestCase):
    """Integration tests for custom template tags"""
    
    def test_custom_tags_loaded(self):
        """Test that custom_tags can be loaded"""
        template = Template('{% load custom_tags %}Success')
        rendered = template.render(Context({}))
        self.assertEqual(rendered, 'Success')
    
    def test_multiple_calculations_in_template(self):
        """Test multiple percentage calculations in one template"""
        template = Template(
            '{% load custom_tags %}'
            '{{ pages1|calculate_percentage:read1 }}-'
            '{{ pages2|calculate_percentage:read2 }}'
        )
        
        context = Context({
            'pages1': 100, 'read1': 25,
            'pages2': 200, 'read2': 50
        })
        rendered = template.render(context)
        
        self.assertEqual(rendered.strip(), '25.0-25.0')
    
    def test_filter_with_variable_names(self):
        """Test filter with different variable naming"""
        template = Template(
            '{% load custom_tags %}'
            '{{ total_pages|calculate_percentage:pages_read }}'
        )
        
        context = Context({
            'total_pages': 400,
            'pages_read': 100
        })
        rendered = template.render(context)
        
        self.assertEqual(rendered.strip(), '25.0')
    
    def test_filter_with_integers(self):
        """Test filter with integer literals"""
        template = Template(
            '{% load custom_tags %}'
            '{{ 100|calculate_percentage:50 }}'
        )
        
        rendered = template.render(Context({}))
        self.assertEqual(rendered.strip(), '50.0')


class CustomTagsEdgeCasesTestCase(TestCase):
    """Edge case tests for custom template tags"""
    
    def test_calculate_percentage_with_one(self):
        """Test percentage with 1 page"""
        result = calculate_percentage(1, 1)
        self.assertEqual(result, 100.0)
    
    def test_calculate_percentage_more_than_total(self):
        """Test when read exceeds total (shouldn't happen but test it)"""
        result = calculate_percentage(100, 150)
        self.assertEqual(result, 150.0)  # Returns > 100%
    
    def test_calculate_percentage_very_small_numbers(self):
        """Test with very small numbers"""
        result = calculate_percentage(10, 1)
        self.assertEqual(result, 10.0)
    
    def test_calculate_percentage_with_floats(self):
        """Test that filter handles float inputs"""
        result = calculate_percentage(100.0, 50.0)
        self.assertEqual(result, 50.0)


class CustomTagsUseCaseTestCase(TestCase):
    """Real-world use case tests"""
    
    def test_book_reading_progress(self):
        """Test typical book reading progress scenario"""
        # Book with 350 pages, read 175
        result = calculate_percentage(350, 175)
        self.assertEqual(result, 50.0)
    
    def test_course_completion(self):
        """Test course completion scenario"""
        # Course with 20 modules, completed 15
        result = calculate_percentage(20, 15)
        self.assertEqual(result, 75.0)
    
    def test_download_progress(self):
        """Test download progress scenario"""
        # 1000 MB total, 250 MB downloaded
        result = calculate_percentage(1000, 250)
        self.assertEqual(result, 25.0)
    
    def test_task_completion(self):
        """Test task completion scenario"""
        # 8 tasks, 6 completed
        result = calculate_percentage(8, 6)
        self.assertEqual(result, 75.0)
