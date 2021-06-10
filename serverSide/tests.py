from django.http import response
from django.test import TestCase, Client
from serverSide import models
from serverSide.models import User, Directory, File, SectionCategory, StatusData, StatusSection, FileSection
from serverSide.forms import DirectoryCreate, FileCreate
from time import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from serverSide.forms import FileCreate
from django.urls import reverse
from serverSide import templates
from django.contrib.auth.models import User
from serverSide.utils import addExtra, getCommand

class ViewNoSetUpTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        models.User.objects.create (
            name="kuba",
            login="kuba",
            password="123"
        )

    def test_indexGet(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_fileCreatePost(self):
        response = self.client.post(reverse('file_create'))
        self.assertEqual(response.status_code, 200)

    def test_deletionGet(self):
        response = self.client.get(reverse('delete'))
        self.assertEqual(response.status_code, 200)

    def test_deleteJs(self):
        response = self.client.get(reverse('delete_js'))
        self.assertEqual(response.status_code, 200)

class ModelTestCase(TestCase):
    def setUp(self):
        user = models.User.objects.create (
            name="kuba",
            login="kuba",
            password="123"
        )
        dire = Directory.objects.create (
            name="abc",
            description="test",
            availability=False,
            owner=user,
            path="/abc",
            level="",
        )
        Directory.objects.create (
            name="cat",
            description="test1",
            owner=user,
            path="/abc/cat",
            level="--",
            parentDirectory=dire
        )
        f = File.objects.create (
            name="file",
            availability=False,
            ffile=SimpleUploadedFile("text.txt", ""),
            directory=dire,
            validity=False
        )
        File.objects.create (
            name="file2",
            ffile=SimpleUploadedFile("text2.txt", ""),
            directory=dire,
        )
        categ = SectionCategory.objects.create (
            category="invariant"
        )
        categ2 = SectionCategory.objects.create (
            category="variant"
        )
        statu = StatusSection.objects.create (
            status="Failed"
        )
        statData = StatusData.objects.create (
            statusDataField="Failed because of...",
            user=user
        )
        FileSection.objects.create (
            name="inv",
            description="hello",
            category=categ,
            status=statu,
            statusData=statData,
            parentFile=f,
            sectBegin=0,
            sectEnd=10
        )
        FileSection.objects.create (
            name="var",
            category=categ2,
            parentFile=f,
            sectBegin=11,
            sectEnd=20
        )

    def test_user(self):
        kuba = models.User.objects.get(name="kuba")
        self.assertEqual(getattr(kuba, "login"), "kuba")
        self.assertEqual(getattr(kuba, "password"), "123")
        self.assertEqual(kuba.__str__(), "kuba")

    def test_dir(self):
        user = models.User.objects.get(name="kuba")
        abc = Directory.objects.get(name="abc")
        cat = Directory.objects.get(name="cat")
        f = File.objects.get(name="file")
        f2 = File.objects.get(name="file2")
        self.assertEqual(getattr(abc, "owner"), user)
        self.assertEqual(getattr(cat, "owner"), user)
        self.assertEqual(getattr(abc, "description"), "test")
        self.assertEqual(getattr(cat, "description"), "test1")
        self.assertEqual(getattr(abc, "path"), "/abc")
        self.assertEqual(getattr(cat, "path"), "/abc/cat")
        self.assertEqual(getattr(abc, "availability"), False)
        self.assertEqual(getattr(cat, "availability"), True)
        self.assertEqual(getattr(cat, "parentDirectory"), abc)
        self.assertEqual(getattr(abc, "parentDirectory"), None)
        files = abc.files.all()
        self.assertEqual(files.filter(name="file")[0], f)
        self.assertEqual(files.filter(name="file2")[0], f2) 

    def test_file(self):
        dire = Directory.objects.get(name="abc")
        f = File.objects.get(name="file")
        f2 = File.objects.get(name="file2")
        self.assertEqual(getattr(f, "description"), "")
        self.assertEqual(getattr(f, "availability"), False)
        self.assertEqual(getattr(f, "validity"), False)
        self.assertEqual(getattr(f, "directory"), dire)
        self.assertEqual(getattr(f2, "directory"), dire)
        self.assertEqual(f.__str__(), "file")

    def test_category(self):
        categ = SectionCategory.objects.get(category="invariant")
        self.assertEqual(getattr(categ, "category"), "invariant")
        self.assertEqual(categ.__str__(), "1invariant")

    def test_status(self):
        statu = StatusSection.objects.get(status="Failed")
        self.assertEqual(getattr(statu, "status"), "Failed")

    def test_statusdata(self):
        statData = StatusData.objects.get(statusDataField="Failed because of...")
        kuba = models.User.objects.get(name="kuba")
        self.assertEqual(getattr(statData, "statusDataField"), "Failed because of...")
        self.assertEqual(getattr(statData, "user"), kuba)

    def test_filesection(self):
        categ = SectionCategory.objects.get(category="invariant")
        statu = StatusSection.objects.get(status="Failed")
        statData = StatusData.objects.get(statusDataField="Failed because of...")
        f = File.objects.get(name="file")
        section = FileSection.objects.get(name="inv")
        section2 = FileSection.objects.get(name="var")
        self.assertEqual(getattr(section, "description"), "hello")
        self.assertEqual(getattr(section, "category"), categ)
        self.assertEqual(getattr(section, "status"), statu)
        self.assertEqual(getattr(section, "statusData"), statData)
        self.assertEqual(getattr(section, "parentFile"), f)
        self.assertEqual(getattr(section, "sectBegin"), 0)
        self.assertEqual(getattr(section, "sectEnd"), 10)
        self.assertEqual(getattr(section2, "parentFile"), f)
        sections = f.sections.all()
        self.assertEqual(sections.filter(name="inv")[0], section)
        self.assertEqual(sections.filter(name="var")[0], section2)
        self.assertEqual(section.__str__(), "1 0 10")

class FormTestCase(TestCase):
    def setUp(self):
        user = models.User.objects.create (
            name="kuba",
            login="kuba",
            password="123"
        )
        Directory.objects.create (
            name="abc",
            description="test",
            availability=False,
            owner=user,
            path="/abc",
            level="",
        )

    def test_formcorrectness_directory(self):
        form = DirectoryCreate()
        self.assertIsNotNone(form.fields["name"])
        self.assertIsNotNone(form.fields["description"])
        self.assertIsNotNone(form.fields["parentDirectory"])

    def test_formcorrectness_file(self):
        form = FileCreate()
        self.assertIsNotNone(form.fields["name"])
        self.assertIsNotNone(form.fields["description"])
        self.assertIsNotNone(form.fields["ffile"])
        self.assertIsNotNone(form.fields["directory"])

    def test_illegalsign(self):
        dire = Directory.objects.get(name="abc")        
        form = FileCreate(data= {
            "name": "illegalSign;",
            "ffile": SimpleUploadedFile("tex;t.txt", ""),
            "directory": dire})

        self.assertEqual(form.is_valid(), False)

    def test_illegalsign2(self):
        dire = Directory.objects.get(name="abc")
        form = FileCreate(data= {
            "name": "illegalSign)",
            "ffile": SimpleUploadedFile("tex)t.txt", ""),
            "directory": dire})

        self.assertEqual(form.is_valid(), False)

    def test_whitespace(self):
        dire = Directory.objects.get(name="abc")
        form = FileCreate(data= {
            "name": "illegalSignSpace",
            "ffile": SimpleUploadedFile("tex t.txt", ""),
            "directory": dire})

        self.assertEqual(form.is_valid(), False)

    def test_nodirectory(self):
        form = FileCreate(data= {
            "name": "nodir",
            "ffile": SimpleUploadedFile("text.txt", "")})

        self.assertEqual(form.is_valid(), False)

    def test_form_inputs(self):
        dire = Directory.objects.get(name="abc")
        response = self.client.post("/dir_create/", data={
            "name": "dirtest",
            "parentDirectory" : dire}
        )

        self.assertEqual(response.status_code, 302)

    def test_form_file_inputs(self):
        dire = Directory.objects.get(name="abc")
        response = self.client.post("/file_create/", data={
            "name": "illegalSignSpace",
            "ffile": SimpleUploadedFile("text.txt", ""),
            "directory": dire}
        )

        self.assertEqual(response.status_code, 302)

class ViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        user = models.User.objects.create (
            name="john",
            login="john",
            password="123"
        )
        dire = Directory.objects.create (
            name="abc",
            description="test",
            availability=True,
            owner=user,
            path="/abc",
            level="",
        )
        f = File.objects.create (
            name="file",
            availability=True,
            ffile=SimpleUploadedFile("text.txt", ""),
            directory=dire,
            validity=False
        )

    def test_indexGET_loginredirect(self):
        self.client.logout()
        response = self.client.get(reverse('index'))
        self.assertEqual(response['location'], "/login/?next=/index/")
        self.assertEqual(response.status_code, 302)

    def test_indexGet(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/index.html')
        self.assertEqual(response.context['tab'], "")
        self.assertEqual(response.context['frama'], [])
        self.assertEqual(response.context['overlaps'], ["overlap", "overlap", "overlap"])
        self.assertEqual(response.context['content'], "Choose a file!")

    def test_logout_redirect(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response['location'], "/logout")
        self.assertEqual(response.status_code, 302)

    def test_preindex(self):
        response = self.client.get(reverse('preindex'))
        self.assertEqual(response['location'], "/index/")
        self.assertEqual(response.status_code, 302)

    def test_saveprover_redirect(self):
        response = self.client.get(reverse('saveProv'))
        self.assertEqual(response['location'], "/show_tab/prover/")
        self.assertEqual(response.status_code, 302)

    def test_filedelete_incorrect(self):
        response = self.client.get(reverse('fileDelete', args=[1000]))
        self.assertEqual(response.status_code, 404)

    def test_filedelete_correct(self):
        response = self.client.get(reverse('fileDelete', args=[1]))
        self.assertEqual(response.status_code, 302)

    def test_directorydelete_incorrect(self):
        response = self.client.get(reverse('directoryDelete', args=[1000]))
        self.assertEqual(response.status_code, 404)

    def test_directorydelete_correct(self):
        response = self.client.get(reverse('directoryDelete', args=[1]))
        self.assertEqual(response.status_code, 302)

    def test_savevc_redirect(self):
        response = self.client.get(reverse('saveVc'))
        self.assertEqual(response['location'], "/show_tab/vcs/")
        self.assertEqual(response.status_code, 302)

    def test_savevc(self):
        response = self.client.post(reverse('saveVc'), {'rte' : "true", 'vcs' : "inwariat"})
        self.assertEqual(response.status_code, 302)

    def test_saveprover(self):
        response = self.client.post(reverse('saveProv'), {'provers' : "alfhazero"})
        self.assertEqual(response.status_code, 302)

    def test_delete(self):
        response = self.client.get(reverse('delete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/delete.html')
        self.assertIsNotNone(response.context['all_dire'])

    def test_createfile(self):
        response = self.client.get(reverse('file_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/create.html')
        self.assertIsNotNone(response.context['form'])

    def test_createdirectory(self):
        response = self.client.get(reverse('dir_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/create.html')
        self.assertIsNotNone(response.context['form'])

    def test_compile_redirect(self):
        session = self.client.session
        session['prev'] = "-1"
        session.save()
        response = self.client.get(reverse('compile'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "/index/")

    def test_compile(self):
        session = self.client.session
        session['prev'] = "1"
        session['prover'] = "None"
        session['rte'] = "No"
        session['vc'] = "None"
        session['1'] = {'parsedFrama' : ""}
        session.save()
        response = self.client.get(reverse('compile'))
        self.assertEqual(response.status_code, 200)

    def test_showTabProver_incorrect(self):
        session = self.client.session
        session['prev'] = "-1"
        session.save()
        response = self.client.get(reverse('showTab', args=['prover']))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "/index/")

    def test_showTabProver_correct(self):
        session = self.client.session
        session['prev'] = "0"
        session["0"] = {
            'extra' : "",
            'content' : "a",
            'frama' : ["2"]
        }
        session.save()
        response = self.client.get(reverse('showTab', args=['prover']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/index.html')
        self.assertEqual(response.context['content'], "a")
        self.assertEqual(response.context['extra'], "")
        self.assertIsNone(response.context['frama'])
        self.assertIsNotNone(response.context['all_dire'])
        self.assertEqual(response.context['overlaps'], ["overlap-active", "overlap", "overlap"])

    def test_showTabVc_incorrect(self):
        session = self.client.session
        session['prev'] = "-1"
        session.save()
        response = self.client.get(reverse('showTab', args=['vcs']))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "/index/")

    def test_showTabVc_correct(self):
        session = self.client.session
        session['prev'] = "0"
        session["0"] = {
            'extra' : "",
            'content' : "a",
            'frama' : ["2"]
        }
        session.save()
        response = self.client.get(reverse('showTab', args=['vcs']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/index.html')
        self.assertEqual(response.context['content'], "a")
        self.assertEqual(response.context['extra'], "")
        self.assertIsNone(response.context['frama'])
        self.assertIsNotNone(response.context['all_dire'])
        self.assertEqual(response.context['overlaps'], ["overlap", "overlap-active", "overlap"])

    def test_showTabResult_incorrect(self):
        session = self.client.session
        session['prev'] = "-1"
        session.save()
        response = self.client.get(reverse('showTab', args=['result']))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "/index/")

    def test_showTabResult_correct_nofile(self):
        session = self.client.session
        session['prev'] = "0"
        session["0"] = {
            'extra' : "",
            'content' : "a",
            'frama' : ["2"]
        }
        session.save()
        response = self.client.get(reverse('showTab', args=['result']))
        self.assertEqual(response.status_code, 404)

    def test_showTabResult_correct_file(self):
        session = self.client.session
        session['prev'] = "1"
        session["1"] = {
            'extra' : "",
            'content' : "a",
            'frama' : ["2"]
        }
        session.save()
        response = self.client.get(reverse('showTab', args=['result']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/index.html')
        self.assertEqual(response.context['content'], "a")
        self.assertEqual(response.context['extra'], "")
        self.assertIsNone(response.context['frama'])
        self.assertIsNotNone(response.context['all_dire'])
        self.assertEqual(response.context['overlaps'], ["overlap", "overlap", "overlap-active"])

    def test_showfile_nofile(self):
        response = self.client.get(reverse('showFile', args=[1000]))
        self.assertEqual(response.status_code, 404)

    def test_showfile(self):
        response = self.client.get(reverse('showFile', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index/index.html')
        self.assertEqual(response.context['content'], "")
        self.assertIsNotNone(response.context['frama'])
        self.assertIsNotNone(response.context['all_dire'])
        self.assertEqual(response.context['overlaps'], ["overlap", "overlap", "overlap"])

    def test_JS(self):
        response = self.client.get(reverse('show_file_js'), {"pk" : 1})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('delete_js'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('delete_file_js'), {"pk" : 1})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('delete_dir_js'), {"pk" : 1})
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        session['prev'] = "1"
        session['prover'] = "None"
        session['rte'] = "No"
        session['vc'] = "None"
        session['1'] = {'parsedFrama' : ""}
        session.save()
        response = self.client.get(reverse('compile_js'))
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        session['prev'] = "-1"
        session.save()
        response = self.client.get(reverse('compile_js'))
        self.assertEqual(response.status_code, 200)

class UtilsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        user = models.User.objects.create (
            name="john",
            login="john",
            password="123"
        )
        dire = Directory.objects.create (
            name="abc",
            description="test",
            availability=False,
            owner=user,
            path="/abc",
            level="",
        )
        Directory.objects.create (
            name="cat",
            description="test1",
            owner=user,
            path="/abc/cat",
            level="--",
            parentDirectory=dire
        )

    def test_addExtra(self):
        dire = Directory.objects.get(name="abc")
        dire2 = Directory.objects.get(name="cat")
        newDire = addExtra(dire, "john")
        self.assertEqual(getattr(newDire, "path"), "abc/")
        newDire = addExtra(dire2, "john")
        self.assertEqual(getattr(newDire, "path"), "/abccat/")

    def test_getCommand(self):
        comm = getCommand("c4", "Yes", "inwariat", "/home/abc")
        self.assertEqual(comm, 'frama-c -wp -wp-prover c4 -wp-prop="inwariat" -wp-rte /home/abc')

    


        
