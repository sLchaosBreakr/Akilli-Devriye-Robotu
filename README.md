# Akıllı Devriye Robotu

**ROS 2 Jazzy ve Gazebo Harmonic ile Otonom Güvenlik Robotu Simülasyonu**

## 👤 Öğrenci Bilgileri
* **Ad Soyad:** Mustafa Selman Uğuz
* **Öğrenci Numarası:** 22370031083
* **Üniversite:** Necmettin Erbakan Üniversitesi

## 📖 Proje Tanımı ve Amaç
Bu proje, ROS 2 tabanlı, 6 waypoint üzerinden sürekli devriye atan otonom bir mobil robot simülasyonudur. Temel amacı, "Kasa Odası" ve "Sunucu Odası" gibi kritik yasak bölgelerin (Restricted Zones) 7/24 kesintisiz olarak izlenmesidir. Sistem, yasaklı bölgede 5 saniyeden uzun süre kalan nesneleri tespit etme ve otomatik alarm tetikleme algoritmasına sahiptir. Dinamik durum kontrolü sayesinde tehdit anında olay yerine hızlı intikal (0.6 m/s) ve durum analizi gerçekleştirebilmektedir.

## 🎥 Sistem Çalışma Videosu
Sistemin otonom devriye, ihlal tespiti ve hızlı intikal senaryolarını çalışırken görmek için repo dizininde bulunan `calisma_videosu.mp4` dosyasını inceleyebilirsiniz.

## 🚀 Kullanılan Teknolojiler
* **ROS 2 Jazzy Jalisco:** Güçlü middleware ve donanım soyutlaması. Node'lar arası publish/subscribe mimarisi ile gerçek zamanlı, güvenilir ve eşzamanlı veri iletişimi sağlar.
* **Gazebo Harmonic:** Gelişmiş fizik motoru. Gerçek dünya dinamiklerini yansıtan endüstriyel depo ortamı ve yüksek doğruluklu sensör (LiDAR, Odometri, Kamera) simülasyonu sunar.
* **Python:** Devriye kontrolü, yasak bölge izleme, nesne oluşturma ve alarm yönetimi node'larının geliştirilmesinde kullanılmıştır.

## 🏗 Dağıtık Sistem Mimarisi
Sistem iki ana katmandan oluşmaktadır:
* **Sensör ve Navigasyon Katmanı:** Donanımdan (simüle edilmiş) alınan LiDAR ve Odometri verileri, Nav2 (Navigation 2) yığını tarafından işlenir. Bu katman; haritalama, yerelleştirme (AMCL), global ve lokal rota planlaması ile dinamik engellerden kaçınma işlemlerini otonom olarak gerçekleştirir.
* **Karar ve Güvenlik Katmanı:** Sistemin beynini oluşturan özel geliştirilmiş node'lar, ROS 2 Publish/Subscribe ve Action/Service mimarisini kullanarak anlık verileri işler. İhlal tespiti yapıldığında üst düzey acil durum kararlarını alıp navigasyon katmanına iletir.

## ⚙️ ROS 2 Düğüm (Node) Yapısı
* **`patrol_node`:** Robotun ana devriye döngüsünü yönetir. Önceden belirlenmiş 6 waypoint noktasını Nav2 Action Server'a gönderir ve robotun standart hız profilini kontrol eder.
* **`zone_monitor`:** LiDAR ve TF (Transform) verilerini çapraz kontrol ederek Kasa ve Sunucu odalarını tarar. Bölgede bir nesne tespit edilirse 5 saniyelik zamanlayıcıyı başlatır ve ihlal durumunda sinyal üretir.
* **`object_spawner`:** Simülasyon testleri için kontrollü nesne (örneğin izinsiz bir koli veya kişi simetrisi) oluşturur. Yasak bölgelere dinamik olarak obje yerleştirerek sistemin tepkisini ölçmeyi sağlar.
* **`alert_manager`:** Alarm durumlarının merkezi koordinatörüdür. İhlal onaylandığında robotun hızını anlık olarak 0.3 m/s'den 0.6 m/s'ye çıkarır ve devriyeyi kesip hedef alana yönlendirir.

## 🚨 Otonom Müdahale Senaryosu
1.  **Normal Devriye:** Robot, harita üzerindeki 6 waypoint arasında standart güvenlik prosedürü olan 0.3 m/s hızla devriye gezer.
2.  **İhlal Tespiti:** Yasak bölgede (Kasa/Sunucu Odası) izinsiz bir nesne tespit edilir ve 5 saniye kuralı aşıldığında alarm tetiklenir.
3.  **Hızlı İntikal:** Sistem Acil Durum moduna geçer, robot hızı 0.6 m/s'ye yükseltilir ve mevcut rotayı bırakıp olay yerine yönelir.
4.  **İnceleme & Dönüş:** Olay yerine varan robot, 3 saniye boyunca alanı analiz eder. Tehdit kalktığında normal devriye döngüsüne geri döner.

## 🏭 Simülasyon Ortamı
Gazebo Harmonic üzerinde tasarlanan simülasyon ortamı, modern bir lojistik deponun tüm fiziksel zorluklarını barındıracak şekilde modellenmiştir. Ortamda forkliftler, endüstriyel raflar, kutular, paletler ve güvenlik masası gibi statik engeller yer almaktadır. Sunucu Odası ve Kasa özel kırmızı yasak alanlar olarak haritalandırılmıştır.

## 🎯 Kazanımlar
Bu proje ile tam otonom bir sistemin kritik altyapıları koruma becerisi test edilmiştir. Olay tabanlı programlama, gerçek zamanlı sensör verilerinin (LiDAR, Kamera, TF) işlenmesi, Nav2 entegrasyonu ve karmaşık durumlarda otonom karar verme yeteneği başarıyla uygulanmıştır. Sistem mimarisi, gerçek dünyadaki depo ve tesis güvenliği ihtiyaçlarına doğrudan uyarlanabilir niteliktedir.
