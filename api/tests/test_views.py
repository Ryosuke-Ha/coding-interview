from django.urls import reverse
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="株式会社テスト１")

    def test_list(self):
        category2 = Category.objects.create(company=self.company, name="カテゴリ２")
        category1 = Category.objects.create(company=self.company, name="カテゴリ１", parent_category=category2)
        
        response = self.client.get(reverse("category-list"))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "カテゴリ１")
        self.assertEqual(response.data[0]["company"], self.company.id)
        self.assertEqual(response.data[0]["id"], str(category1.id))
        self.assertEqual(response.data[0]["parent_category"], category2.id)
        self.assertIn("created_at", response.data[0])
        self.assertIn("updated_at", response.data[0])

        self.assertEqual(response.data[1]["name"], "カテゴリ２")
        self.assertEqual(response.data[1]["company"], self.company.id)
        self.assertEqual(response.data[1]["id"], str(category2.id))
        self.assertEqual(response.data[1]["parent_category"], None)
        self.assertIn("created_at", response.data[1])
        self.assertIn("updated_at", response.data[1])

    def test_retrieve(self):
        category = Category.objects.create(company=self.company, name="カテゴリ１")

        response = self.client.get(reverse("category-detail", args=[category.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "カテゴリ１")
        self.assertEqual(response.data["company"], self.company.id)
        self.assertEqual(response.data["id"], str(category.id))
        self.assertEqual(response.data["parent_category"], None)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_create(self):
        response = self.client.post(reverse("category-list"), data={
            "name": "カテゴリ１",
            "company": self.company.id
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "カテゴリ１")
        self.assertEqual(response.data["company"], self.company.id)
        self.assertIn("id", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)
        self.assertEqual(Category.objects.count(), 1)

    def test_update(self):
        category = Category.objects.create(company=self.company, name="カテゴリ１")

        response = self.client.put(reverse("category-detail", args=[category.id]), data={
            "name": "カテゴリ１（更新）",
            "company": self.company.id
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "カテゴリ１（更新）")
        self.assertEqual(response.data["company"], self.company.id)
        self.assertEqual(response.data["id"], str(category.id))
        self.assertEqual(response.data["parent_category"], None)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)
        category.refresh_from_db()
        self.assertEqual(category.name, "カテゴリ１（更新）")

    def test_destroy(self):
        category = Category.objects.create(company=self.company, name="カテゴリ１")

        response = self.client.delete(reverse("category-detail", args=[category.id]))
        
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_create_duplicate(self):
        category = Category.objects.create(company=self.company, name="カテゴリ１")

        response = self.client.post(reverse("category-list"), data={
            "name": category.name,
            "company": category.company.id
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)
    
    def test_retrieve_not_found(self):
        response = self.client.get(reverse("category-detail", args=["00000000-0000-0000-0000-000000000000"]))

        self.assertEqual(response.status_code, 404)

    def test_destroy_keeps_children(self):
        category1 = Category.objects.create(company=self.company, name="カテゴリ１")
        category2 = Category.objects.create(company=self.company, name="カテゴリ２", parent_category=category1)

        response = self.client.delete(reverse("category-detail", args=[category1.id]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=category1.id).exists())
        self.assertTrue(Category.objects.filter(id=category2.id).exists())
        category2.refresh_from_db()
        self.assertIsNone(category2.parent_category)