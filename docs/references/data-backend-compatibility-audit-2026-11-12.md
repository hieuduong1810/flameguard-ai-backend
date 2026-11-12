# Data Team → Backend compatibility audit (Phase 3B)

**Ngày:** 12/11/2026
**Trạng thái:** Bản audit tạm để đọc và quyết định; không phải hợp đồng import đã duyệt.
**Phạm vi:** Chỉ đọc Data Team repository và backend repository. Không chạy ETL/import/test, không đổi database hoặc Phase 4.

## A. Đánh giá tương thích hiện tại

**Tương thích một phần.** Backend có thể biểu diễn investigation, run, điều kiện và phần lớn phép đo số bằng schema hiện tại. Tuy nhiên, chưa thể nhập và công bố nguyên vẹn bộ output của Data Team: phép đo dạng chữ, cờ chất lượng, provenance ở cấp run/measurement, chuỗi thời gian và kết quả ranking chưa có ánh xạ đầy đủ. Phase 4 cũng chưa có cơ chế chấp nhận và công bố collection đã được Data Team duyệt.

[Build report](../../../Nasa-hackathon-dataprocessing/data/unified/BUILD_REPORT.md) ghi **19 investigations, 1.687 runs, 6.574 measurements, 882 mẫu time series, 43 facts và 456 ranking rows**. Đây là số liệu từ báo cáo build có sẵn; audit này không chạy lại ETL hay kiểm chứng khoa học các kết quả. Có 11 investigations có dữ liệu ở cấp run; 8 investigations còn lại hiện chủ yếu là metadata.

Dataset Report nằm tại [Data Team docs](../../../Nasa-hackathon-dataprocessing/docs/Flame%20in%20Freefall%20-%20Dataset%20Report.md). Trước khi tạo file audit này, backend chưa có thư mục `docs/references/`.

## B. Ma trận ánh xạ trường

**Trực tiếp** nghĩa là có cột tương ứng. **Adapter** nghĩa là cần đổi kiểu/đơn vị hoặc tách thành nhiều hàng. **Thiếu** nghĩa là không thể giữ đủ ý nghĩa trong schema hiện tại.

| Data output và trường | Backend đích | Đánh giá và quy tắc |
| --- | --- | --- |
| `experiments.psi_id`, `full_name` | `investigation.psi_id`, `title` | **Trực tiếp.** `experiment_id` cần manifest ánh xạ ổn định tới UUID; public slug là danh tính thứ ba, không thay cho PSI ID. |
| `experiments` purpose/objectives, platform | `investigation.research_purpose`, `platform` | **Adapter**, chỉ khi có metadata nguồn được Data Team xác nhận. Không suy ra platform từ tên hardware. |
| `experiments.pillar[]`, family | `tag` + `investigation_tag` | **Adapter** với từ điển tag và quy tắc phiên bản. |
| `experiments` PI, sensors, hardware, aliases, tier, envelope, report paths, counts | Không có cột catalog tương ứng | **Thiếu** nếu cần lưu/trả từng trường. Không nhét toàn bộ vào `research_purpose` hoặc `platform`. Counts có thể tính lại; envelope chỉ nên suy ra từ các run phù hợp hoặc lưu như metadata có nguồn. |
| `runs.run_id`, `experiment_id`, `psi_id` | `test_run.external_run_key`, `investigation_id` → `investigation.psi_id` | **Adapter.** Tạo UUID riêng; kiểm tra `run_id` duy nhất theo phạm vi đã thống nhất. Schema hiện không áp unique cho external run key. |
| `runs.fuel`, `geometry`, `gravity_g` | `test_run.material_type`, `sample_geometry`, `gravity` | **Adapter có nguy cơ mất chi tiết.** `fuel` không đồng nghĩa mọi trường hợp với material; gravity số và trạng thái unknown cần biểu diễn nhất quán. |
| `runs.campaign`, `date`, `fuel_base`, `fuel_fraction`, `fuel_secondary`, `fraction_basis`, `fuel_phase`, `flame_config`, `size_mm`, `size_kind`, `flow_kind`, `atmosphere_status`, `aging_s`, `notes` | Chủ yếu `test_condition.variable`, `value_numeric`/`value_text`, `unit`, `data_status` | **Adapter**, mỗi thuộc tính thành điều kiện riêng, giữ tên biến, đơn vị và trạng thái gốc. `date`/campaign/notes không có cột run chuyên biệt; cách biểu diễn dưới dạng condition cần được chấp thuận nếu sẽ dùng cho truy vấn. |
| `runs.x_o2`, `x_n2`, `x_co2`, `x_he`, `oxidizer_x_o2`, `pressure_kpa`, `flow_cm_s`, `fuel_velocity_cm_s` | `test_condition` | **Adapter phù hợp.** Giữ mole fraction `0–1`, kPa, cm/s. `oxidizer_x_o2` phải là biến khác ambient `x_o2`; inverse flame có ambient O₂ bằng null. |
| `measurements.metric`, `value`, `unit` | `measurement.observable`, `measured_value`, `unit` | **Trực tiếp sau đổi tên**, dùng Decimal từ chuỗi nguồn. Không đổi số 0, null hoặc đơn vị khi chưa có quy tắc chuyển đổi được duyệt. |
| `measurements.value_text` cho `ignition`, `flame_outcome`, `end_mode`, `cool_flame`, `lifted` | Không có `measurement.value_text` | **Thiếu.** Có thể tạm trình bày như `test_condition.value_text` nhưng sẽ đổi nghĩa measurement thành condition và làm sai nhóm API. Cần quyết định schema/hợp đồng. |
| `measurements.flag`, `provenance`, `source` | Không có cột tương ứng trong `measurement` | **Thiếu, nguy cơ mất dữ liệu.** Các cờ như `reported_zero`, `within_sensor_noise`, `operational_no_ignition` phải đi cùng đúng phép đo. |
| `timeseries.time_s`, `metric`, `value`, `unit`, `source_file` | `measurement.raw_asset_ref` | **Chỉ phù hợp ở mức tham chiếu asset.** Không có bảng mẫu thời gian, channel hoặc trục thời gian. Không biến 882 mẫu thành một scalar measurement. |
| `experiments.doi`, `runs.source`/`source_file` | `source_document.doi`, `source_url`, `document_type`, `version` | **Cần đối soát nguồn.** Citation text và đường dẫn trong repo không tự tạo thành URL tài liệu gốc. Nguồn chi tiết có trong `research/*/SOURCES.md`, record và download manifest, nhưng chưa thành manifest tài liệu chuẩn để nối từng hàng. |
| `facts.statement`, `condition`, `source_ref`, `confidence`, các giá trị/giới hạn/công thức | `evidence_claim.claim_text`, `limitation`; `claim_source` → `source_document` | **Chỉ một phần.** `source_ref` cần giải thành document ID và locator thật. Numeric range, formula, confidence và điều kiện riêng chưa có nơi lưu có cấu trúc. Không tự gọi một fact là claim đã review. |
| `scenarios` | `scenario` | **Adapter**: `x_o2` fraction → `oxygen_pct`; kPa → `pressure_psi`; gravity số → chuỗi đã quy ước. `material` và `ventilation` là cột bắt buộc nhưng Data scenario không cung cấp tương ứng, nên chưa thể tạo bản ghi đầy đủ một cách trung thực. |
| `scenario_priors`, `rankings` | `scenario_match`/`match_dimension` | **Không khớp ngữ nghĩa.** Ranking của Data Team là ở cấp investigation, theo scenario và pillar; `scenario_match` hiện là **scenario → test_run**. Không gán score investigation vào một run bất kỳ. |
| `fuel_properties`, năm view `ml_*` | Chưa có đích persistence tương đương | **Ngoài Phase 4.** Là dữ liệu phụ trợ/đầu vào AI, cần version, nguồn và hợp đồng riêng. View ML có thể cố ý bỏ hoặc đặt NaN cho giá trị bị flag; không dùng thay bảng phép đo gốc. |

Nguồn đối chiếu: [unified schema](../../../Nasa-hackathon-dataprocessing/etl/schema.py), [ETL build](../../../Nasa-hackathon-dataprocessing/etl/build.py), [catalog models](../../app/models/catalog.py), [evidence models](../../app/models/evidence.py), [scenario models](../../app/models/scenarios.py).

## C. Backend gaps

1. **Provenance chưa đủ hạt mịn.** `source_document` thuộc investigation và `claim_source` nối claim với tài liệu/run, nhưng không có liên kết nguồn trực tiếp cho từng run hay measurement. `measurements.source` có thể khác `runs.source`; lấy nguồn của run thay cho measurement sẽ làm sai traceability.
2. **Measurement dạng phân loại và quality flag chưa lưu được đúng chỗ.** Cột số nullable không đủ để bảo tồn `value_text`, `flag` và provenance của phép đo.
3. **Telemetry mới có tham chiếu file.** Cần hợp đồng asset, channel, thời gian, đơn vị, quyền truy cập và phiên bản trước khi có API time series.
4. **Catalog metadata chưa đủ cho trải nghiệm Data Team.** Hardware, sensors, năm, family, tier, envelope và ranking không có DTO hoặc cột tương ứng. Phase 4 hiện trả unavailable cho nhiều trường thay vì bịa dữ liệu.
5. **Admission/publication còn khóa.** [Collection service](../../app/services/collection.py) chỉ nhận synthetic hoặc real/unknown chưa review qua snapshot khớp chính xác 21 bảng và read role; `reviewState=curated` bị từ chối. `seed_demo_data.py` chỉ dành cho dữ liệu synthetic, không phải importer của Data Team.
6. **Nguồn và review chưa chuẩn hóa.** `source_url` là bắt buộc, trong khi `source` ở unified là citation text. Cần URL tài liệu gốc, locator, checksum/version, thời điểm lấy và quyết định curator trước khi công bố. `verifiedRunCount` của Phase 4 vẫn là unknown.
7. **Tài liệu có xung đột cần quyết định.** Tại thời điểm audit, [AGENTS.md](../../AGENTS.md) và [documentation map](../documentation-map.md) gọi ERD là frozen/authoritative. Chính sách này đã được cập nhật trong [ADR-0003](../decisions/ADR-0003-schema-evolution-and-hackathon-prototype.md): ERD 21 bảng là baseline hiện tại, có thể phát triển qua migration được duyệt. [Masterplan](../../../Nasa-hackathon-dataprocessing/Masterplan.md) mô tả E-FIELD như mô phỏng partial gravity, còn Dataset Report bác bỏ phép quy đổi đó. Hai cách tính **usefulness score** (`dataset_catalog`) và **scenario ranking score** (`rank.py`) cũng khác nhau; API phải đặt tên và version riêng, không gọi chung là “score”.

## D. Ranh giới adapter được đề xuất

- **Data Team:** sở hữu ETL, chuẩn hóa khoa học, source manifest, cờ chất lượng, unit dictionary, review và việc thực thi import.
- **Backend Phase 3B:** nhận **export có version**, kiểm tra schema/identity/unit/null/nguồn, tạo kế hoạch ánh xạ UUID–PSI–run key–slug, kiểm tra tính không mất dữ liệu và tạo báo cáo accepted/rejected. Adapter chuyển output đã được duyệt sang persistence schema; không viết lại parser NASA.
- **Read API:** tiếp tục dùng repository/service để đọc dữ liệu đã được chấp nhận. Ranking từ Data Team nên đi qua hợp đồng kết quả có `algorithmVersion`, scenario, pillar, components, data version, caveat; không ngụy trang thành sort Phase 4.
- **Scientific/AI gate:** model, advisor và phép so sánh dẫn xuất cần AI/Data review riêng. Backend chỉ kiểm tra hợp đồng, provenance và điều kiện công bố.

Đối với dataset NASA chính thức khác vào **14/11/2026**, kiến trúc nhiều lớp và `test_condition`/`measurement` dạng long-form giúp hấp thụ **biến số và metric số mới** qua adapter. Khả năng này **không bảo đảm** giữ được loại dữ liệu mới, telemetry, provenance theo hàng, hay ranking theo investigation. Nên chốt hợp đồng mở rộng sau khi xem mẫu chính thức, không thiết kế theo giả định PSI prototype.

## E. Thay đổi schema có thể cần

| Mức | Đề xuất có điều kiện |
| --- | --- |
| Có thể chỉ dùng adapter | Điều kiện số/text mới; đổi đơn vị có chứng từ và giữ bản gốc; tạo UUID ổn định; mapping tag; liên kết `psi_id` với investigation; asset ref ở mức file. |
| Nên xem xét migration | `measurement.value_text`, quality flag/status và provenance hoặc bảng metadata theo measurement; liên kết run/measurement → source document + locator; run date/campaign nếu cần lọc/truy vấn; catalog metadata có cấu trúc; bảng kết quả ranking theo investigation/scenario/pillar/version nếu cần lưu và truy vấn. |
| Chỉ quyết định sau mẫu chính thức | Thiết kế time series/channel/asset; nhiều nguồn cho một observation; uncertainty phức hợp; danh tính/version của dataset; kiểu phép đo mới ngoài scalar/categorical. |

Không sửa các migration `0001–0003`. Nếu được duyệt, tạo revision mới và ghi ADR cùng kế hoạch bảo toàn dữ liệu.

## F. Phase 3B readiness checklist và acceptance tests

1. Data Team giao manifest phiên bản gồm nguồn NASA gốc, URL/DOI, file hash, locator, license/access, timestamp, vocabulary, unit dictionary, review record và known issues.
2. Chốt `experiment_id` ↔ `psi_id` ↔ UUID ↔ slug, cùng phạm vi unique của `run_id`; kiểm tra trùng và thay đổi qua các lần build.
3. Chốt cách lưu categorical measurement, flag, provenance theo hàng và time series trước khi import.
4. Dùng mẫu nhỏ **không ghi DB** để kiểm thử ánh xạ và lập báo cáo field-level loss: mọi trường nguồn phải được lưu, dẫn tới asset/version được quản lý, hoặc được ghi là chưa hỗ trợ.
5. Kiểm thử bắt buộc: inverse flame không thành ambient O₂; null khác 0; CFI `reported_zero` còn flag; BRE operational no-ignition không thành nhãn khoa học; cùng unit nhưng khác phương pháp không bị so sánh dẫn xuất; nguồn từng measurement không bị gán nhầm; DOI/locator có thể truy ngược tài liệu.
6. Sau khi hợp đồng và migration được duyệt, chạy acceptance trên **PostgreSQL test cô lập**, kiểm tra FK, idempotency, retry, raw value/unit/flag/source và API readback. Chỉ công bố collection đã được curator chấp thuận.
7. T078 vẫn là gate **Frontend acceptance** riêng của Phase 4; Phase 3B không tự đóng nó.

## G. Bốn module và mức API hiện có

| Module Data Team | Phase 4 hiện có | Còn thiếu / owner |
| --- | --- | --- |
| **Summarize & Rank** | Investigation list/detail, dashboard, run/condition/measurement/source/claim pages. | Chưa có API ranking theo scenario/pillar, component score, algorithm/data version hoặc summary có nguồn. Data cung cấp kết quả và giải thích; Backend định nghĩa DTO/API sau review. |
| **Compare** | `POST /compare` trả 2–3 investigations và observation gốc; `comparability=not_established`, không tính delta. | Muốn so sánh định lượng cần Data/scientific rule cho cùng observable, unit, geometry, run condition, phương pháp và uncertainty. Backend không tự áp dụng median trong Dataset Report. |
| **Partial-Gravity Predictor** | Chưa có API prediction Phase 4; models lưu version/result chỉ là cấu trúc. | AI Team phải giao model, validation, domain và uncertainty. Không có đo trực tiếp 1/6 g hay 3/8 g trong bộ prototype; E-FIELD không tạo ánh xạ trọng lực. |
| **Prevention–Detection–Suppression Advisor** | Tags, sources, claims và observation có thể cung cấp chứng cứ thô. | Chưa có advice/grounded reasoning API. Data/AI cần fact–source mapping, review và giới hạn suy luận; Backend kiểm tra citation/abstention, không phát lời khuyên an toàn đã xác nhận. |

## H. Có thể hoàn thành trước 14/11

Chốt export manifest và version, bảng ánh xạ trường, identity policy, unit/status vocabulary, danh sách trường mất dữ liệu, mẫu source/locator, contract cho ranking, cùng bộ acceptance tests trên fixtures và test DB cô lập. Có thể thiết kế ADR/migration **đề xuất** cho categorical measurement, provenance và ranking, rồi quyết định sau khi có mẫu chính thức.

## I. Phải chờ dataset chính thức

Xác nhận metric, kiểu dữ liệu, số lượng, provenance, quyền truy cập và danh tính của dataset được ban tổ chức cung cấp; kiểm tra adapter với mẫu thật; quyết định migration cuối cùng; chạy Data Team import và curator review; chứng minh API readback; đánh giá lại ranking, so sánh và phạm vi mô hình. Không thể coi các kết quả PSI prototype là bằng chứng rằng dataset chính thức sẽ cùng cấu trúc hoặc đủ để xác nhận prediction/advice.

## Ghi chú kiểm tra

Audit chỉ đọc. File Markdown này là thay đổi duy nhất của yêu cầu lưu báo cáo. Không chạy import/test, không đổi database, không sửa code, không commit hay push.
