class Asset {
  final int id;
  final int organizationId;
  final String assetCode;
  final int localNumber;
  final String type;
  final String name;
  final String? manufacturer;
  final String? model;
  final String? serialNumber;
  final String? inventoryNumber;
  final int? commissioningYear;
  final String? room;
  final String? responsiblePerson;
  final String? userCategory;
  final String status;
  final String? os;
  final String? description;
  final String? reportCategory;
  final bool isUsedForEducation;
  final bool isAvailableForStudents;
  final bool hasLan;
  final bool hasInternet;
  final bool hasIntranet;
  final bool receivedInCurrentYear;
  final String? ownershipType;
  final bool includeInReports;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final DateTime? deletedAt;

  Asset({
    required this.id,
    required this.organizationId,
    required this.assetCode,
    required this.localNumber,
    required this.type,
    required this.name,
    this.manufacturer,
    this.model,
    this.serialNumber,
    this.inventoryNumber,
    this.commissioningYear,
    this.room,
    this.responsiblePerson,
    this.userCategory,
    required this.status,
    this.os,
    this.description,
    this.reportCategory,
    required this.isUsedForEducation,
    required this.isAvailableForStudents,
    required this.hasLan,
    required this.hasInternet,
    required this.hasIntranet,
    required this.receivedInCurrentYear,
    this.ownershipType,
    required this.includeInReports,
    this.createdAt,
    this.updatedAt,
    this.deletedAt,
  });

  factory Asset.fromJson(Map<String, dynamic> j) => Asset(
        id: j['id'],
        organizationId: j['organization_id'],
        assetCode: j['asset_code'],
        localNumber: j['local_number'],
        type: j['type'],
        name: j['name'],
        manufacturer: j['manufacturer'],
        model: j['model'],
        serialNumber: j['serial_number'],
        inventoryNumber: j['inventory_number'],
        commissioningYear: j['commissioning_year'],
        room: j['room'],
        responsiblePerson: j['responsible_person'],
        userCategory: j['user_category'],
        status: j['status'],
        os: j['os'],
        description: j['description'],
        reportCategory: j['report_category'],
        isUsedForEducation: j['is_used_for_education'] ?? false,
        isAvailableForStudents: j['is_available_for_students'] ?? false,
        hasLan: j['has_lan'] ?? false,
        hasInternet: j['has_internet'] ?? false,
        hasIntranet: j['has_intranet'] ?? false,
        receivedInCurrentYear: j['received_in_current_year'] ?? false,
        ownershipType: j['ownership_type'],
        includeInReports: j['include_in_reports'] ?? true,
        createdAt: DateTime.tryParse(j['created_at'] ?? ''),
        updatedAt: DateTime.tryParse(j['updated_at'] ?? ''),
        deletedAt: j['deleted_at'] == null ? null : DateTime.tryParse(j['deleted_at']),
      );

  /// Тело запроса для создания похожей техники.
  /// Не отправляем id, organization_id, asset_code и local_number — backend создаёт их сам.
  Map<String, dynamic> toCreateJson({bool keepInventoryAndSerial = true}) => {
        'type': type,
        'name': name,
        'manufacturer': manufacturer,
        'model': model,
        'serial_number': keepInventoryAndSerial ? serialNumber : null,
        'inventory_number': keepInventoryAndSerial ? inventoryNumber : null,
        'commissioning_year': commissioningYear,
        'room': room,
        'responsible_person': responsiblePerson,
        'user_category': userCategory,
        'status': status,
        'os': os,
        'description': description,
        'report_category': reportCategory,
        'is_used_for_education': isUsedForEducation,
        'is_available_for_students': isAvailableForStudents,
        'has_lan': hasLan,
        'has_internet': hasInternet,
        'has_intranet': hasIntranet,
        'received_in_current_year': receivedInCurrentYear,
        'ownership_type': ownershipType,
        'include_in_reports': includeInReports,
      };
}

class AssetListResponse {
  final List<Asset> items;
  final int total;
  final int page;
  final int pageSize;
  final int pages;

  AssetListResponse({required this.items, required this.total, required this.page, required this.pageSize, required this.pages});

  factory AssetListResponse.fromJson(Map<String, dynamic> j) => AssetListResponse(
        items: (j['items'] as List).map((e) => Asset.fromJson(e)).toList(),
        total: j['total'],
        page: j['page'],
        pageSize: j['page_size'],
        pages: j['pages'],
      );
}

class AssetStatsResponse {
  final int total;
  final Map<String, int> byStatus;
  final Map<String, int> byType;
  final Map<String, int> byReportCategory;

  AssetStatsResponse({
    required this.total,
    required this.byStatus,
    required this.byType,
    required this.byReportCategory,
  });

  factory AssetStatsResponse.fromJson(Map<String, dynamic> j) => AssetStatsResponse(
        total: j['total'] ?? 0,
        byStatus: Map<String, int>.from(j['by_status'] ?? const <String, int>{}),
        byType: Map<String, int>.from(j['by_type'] ?? const <String, int>{}),
        byReportCategory: Map<String, int>.from(j['by_report_category'] ?? const <String, int>{}),
      );
}


const assetTypes = ['computer', 'laptop', 'monitor', 'printer', 'mfu', 'projector', 'interactive_board', 'tablet', 'server', 'network_device', 'ups', 'other'];
const assetStatuses = ['in_use', 'in_storage', 'in_repair', 'needs_repair', 'written_off', 'lost'];
const userCategories = ['teacher', 'student', 'administration', 'it_staff', 'shared', 'other'];
const reportCategories = ['desktop_pc', 'laptop', 'tablet', 'terminal', 'info_terminal', 'projector', 'interactive_board', 'printer', 'scanner', 'mfu', 'copier', 'other', 'not_included'];
const ownershipTypes = ['own', 'rent', 'use', 'other'];
const userRoles = ['admin', 'editor', 'viewer'];

String dictLabel(String v) => {
      'computer': 'Компьютер',
      'laptop': 'Ноутбук',
      'monitor': 'Монитор',
      'printer': 'Принтер',
      'mfu': 'МФУ',
      'projector': 'Проектор',
      'interactive_board': 'Интерактивная доска',
      'tablet': 'Планшет',
      'server': 'Сервер',
      'network_device': 'Сетевое оборудование',
      'ups': 'ИБП',
      'other': 'Другое',
      'in_use': 'В использовании',
      'in_storage': 'На складе',
      'in_repair': 'В ремонте',
      'needs_repair': 'Требует ремонта',
      'written_off': 'Списано',
      'lost': 'Утеряно',
      'teacher': 'Педагогические работники',
      'student': 'Обучающиеся',
      'administration': 'Администрация',
      'it_staff': 'ИТ-специалисты',
      'shared': 'Общее использование',
      'desktop_pc': 'Стационарный компьютер',
      'terminal': 'Терминал',
      'info_terminal': 'Информационный терминал',
      'scanner': 'Сканер',
      'copier': 'Ксерокс / копир',
      'not_included': 'Не включать в раздел 2.1 ОО-2',
      'own': 'Собственность',
      'rent': 'Аренда',
      'use': 'Безвозмездное пользование',
      'admin': 'Администратор',
      'editor': 'Редактор',
      'viewer': 'Наблюдатель',
      'created': 'Создание карточки',
      'updated': 'Обновление',
      'status_changed': 'Изменение статуса',
      'room_changed': 'Изменение кабинета',
      'responsible_changed': 'Изменение ответственного',
      'user_category_changed': 'Изменение категории пользователей',
      'os_changed': 'Изменение ОС',
      'description_changed': 'Изменение описания',
      'manual_note': 'Ручная заметка',
      'deleted': 'Удаление',
      'restored': 'Восстановление',
    }[v] ?? v;

String reportCategoryLabel(String v) => {
      'desktop_pc': 'стр. 01 — стационарный ПК',
      'laptop': 'стр. 02 — ноутбук / нетбук / портативный ПК',
      'tablet': 'стр. 03 — планшетный компьютер',
      'terminal': 'стр. 01 — терминал ПК',
      'info_terminal': 'стр. 08 — инфомат / информационный киоск',
      'projector': 'стр. 10 — мультимедийный проектор',
      'interactive_board': 'стр. 11 — интерактивная доска',
      'printer': 'стр. 12 — принтер',
      'scanner': 'стр. 13 — сканер',
      'mfu': 'стр. 14 — МФУ',
      'copier': 'стр. 15 — ксерокс / копир',
      'other': 'Другое — проверить вручную, не входит в строки ОО-2 2.1',
      'not_included': 'Не включать в раздел 2.1 ОО-2',
    }[v] ?? dictLabel(v);

String choiceLabel(String field, String value) => field == 'report_category' ? reportCategoryLabel(value) : dictLabel(value);

String fieldLabel(String v) => {
      'type': 'Тип техники',
      'name': 'Название',
      'manufacturer': 'Производитель',
      'model': 'Модель',
      'serial_number': 'Серийный номер',
      'inventory_number': 'Инвентарный номер',
      'commissioning_year': 'Год ввода в эксплуатацию',
      'room': 'Кабинет',
      'responsible_person': 'Ответственный',
      'user_category': 'Категория пользователей',
      'status': 'Статус',
      'os': 'Операционная система',
      'description': 'Описание',
      'report_category': 'Категория ОО-2',
      'is_used_for_education': 'Используется в образовательном процессе',
      'is_available_for_students': 'Доступно обучающимся',
      'has_lan': 'ПК входит в локальную вычислительную сеть',
      'has_internet': 'ПК имеет доступ к Интернету',
      'has_intranet': 'ПК имеет доступ к Интранет-порталу организации',
      'received_in_current_year': 'Получено / приобретено в отчётном году',
      'ownership_type': 'Право владения',
      'include_in_reports': 'Включать в отчёты',
    }[v] ?? v;

String? fieldHelp(String v) => {
      'report_category': 'Выберите строку раздела 2.1 ОО-2, куда должна попасть техника. Для ПК используйте строки 01–07, для проекторов/досок/принтеров/МФУ — строки 10–15.',
      'is_used_for_education': 'Графа 4: техника используется на уроках, при подготовке занятий или домашних заданий.',
      'is_available_for_students': 'Графа 5: техника доступна обучающимся в свободное от основных занятий время.',
      'has_lan': 'Строка 04: локальная сеть — два и более ПК в пределах здания/соседних зданий. Один ПК, подключенный только к принтеру, локальной сетью не считается.',
      'has_internet': 'Строка 05: доступ к Интернету есть напрямую или через шлюз локальной сети. Способ подключения не важен.',
      'has_intranet': 'Строка 06: доступ к внутреннему Интранет-порталу школы через браузер. Это не Интернет, а внутренний ресурс организации.',
      'received_in_current_year': 'Строка 07: техника приобретена, взята в аренду, пользование или получена на иных условиях в отчётном году.',
      'include_in_reports': 'Если выключить, техника не попадёт в расчёт отчёта ОО-2.',
    }[v];
