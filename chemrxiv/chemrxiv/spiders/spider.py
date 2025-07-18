import scrapy
from chemrxiv.items import ChemrxivItem
import json

class SpiderSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = ["chemrxiv.org"]

    def start_requests(self):
        url = "https://chemrxiv.org/engage/api-gateway/chemrxiv/graphql"

        query = """
            query searchDashboardPageLoad(
                $text: String = ""
                $subjects: [String!]
                $categories: [String!]
                $events: [String!]
                $publishedDates: [String!]
                $partners: [String!]
                $contents: [String!]
                $keywords: [String!]
                $authors: String = ""
                $skip: Int = 0
                $limit: Int = 10
                $sortBy: SortByEnum = RELEVANT_DESC
            ) {
                viewer {
                    usageEventsDisabled

                    user {
                    ...userRoleFragment
                    }

                    searchItems(
                    searchTerm: $text
                    subjectKeys: $subjects
                    categoryKeys: $categories
                    eventKeys: $events
                    publishedDateKeys: $publishedDates
                    partnerKeys: $partners
                    contentTypeKeys: $contents
                    keywordsKeys: $keywords
                    searchAuthor: $authors
                    skip: $skip
                    limit: $limit
                    sortBy: $sortBy
                    includeBuckets: true
                    ) {
                        totalCount

                        results: itemHits {
                            highlight {
                                text
                                matchPositions {
                                    start
                                    end
                                }
                            }

                            item {
                            ...itemMatchFragment
                            }
                        }

                        subjectBuckets {
                            ...searchBucketFragment
                        }

                        categoryBuckets {
                            ...searchBucketFragment
                        }

                        eventBuckets {
                            ...searchBucketFragment
                        }

                        partnerBuckets {
                            ...searchBucketFragment
                        }

                        publishedDateBuckets {
                            ...searchBucketFragment
                        }

                        contentBuckets: contentTypeBuckets {
                            ...searchBucketFragment
                        }

                        dateBuckets: publishedDateBuckets {
                            ...searchBucketFragment
                        }
                    }

                    subjectTypes: subjects {
                        ...subjectTypeFragment
                    }

                    contentTypes {
                        ...contentTypeFragment
                    }

                    categoryTypes: categories {
                        ...categoryTypeFragment
                    }
                }
            }

            fragment userRoleFragment on User {
                __typename
                id
                sessionExpiresAt
                titleTypeId: title
                firstName
                lastName
                emailAddress: email
                orcid
                roles
                accountType
            }

            fragment itemMatchFragment on MainItem {
                __typename
                id
                title
                abstract
                keywords
                origin
                version
                publishedDate
                submittedDate
                subjectType: subject {
                    ...subjectTypeFragment
                }
                contentType {
                    ...contentTypeFragment
                }
                categoryTypes: categories {
                    ...categoryTypeFragment
                }
                mainCategory {
                    name
                }
                asset {
                    mimeType
                    original {
                    url
                    }
                }
                authors {
                    title
                    firstName
                    lastName
                    authorConfirmationId
                    displayOrder
                }
                metrics {
                    metricType
                    description
                    value
                    unit
                }
                citationsCount
                community {
                    id
                    name
                }
            }

            fragment searchBucketFragment on SearchBucket {
                __typename
                count
                key
                label
            }

            fragment subjectTypeFragment on Subject {
                __typename
                id
                name
                description
            }

            fragment contentTypeFragment on ContentType {
                __typename
                id
                name
                allowSubmission
                allowJournalSubmission
                allowCommunitySubmission
                allowResearchDirectionSubmission
                videoAllowedCheck
                allowedFileTypes
                allowedVideoFileTypes
            }

            fragment categoryTypeFragment on Category {
                __typename
                id
                name
                description
                parentId
            }

        """

        payload = {
            "operationName": "searchDashboardPageLoad",
            "variables": {
                "text": "electrolyte",
                "sortBy": "PUBLISHED_DATE_DESC",
                "skip": 0,
                "authors": "",
                "categories": [],
                "contents": [],
                "events": [],
                "publishedDates": [],
                "subjects": [],
                "partners": [],
                "keywords": []
            },
            "query": query
        }
        yield scrapy.Request(
            url=url,
            method="POST",
            body=json.dumps(payload),
            headers = {
                "Content-Type": "application/json",
                "x-api-key": "y6nWHrymZysXc",
                "x-apollo-operation-name": "searchDashboardPageLoad",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
            },
            callback=self.parse,
            meta={"skip": 0, "query": query}
        )

    def parse(self, response):
        data = json.loads(response.text)
        results = (
            data.get("data", {})
            .get("viewer", {})
            .get("searchItems", {})
            .get("results", [])
        )
        for record in results:
            item_data = record.get("item", {})
            item = ChemrxivItem()
            item["title"] = item_data.get("title")
            item["authors"] = [
                f"{a.get('firstName', '')} {a.get('lastName', '')}"
                for a in item_data.get("authors", [])
            ]
            item["abstract"] = item_data.get("abstract")
            item["date"] = item_data.get("publishedDate")
            item["id"] = item_data.get("id")
            yield item

        search_items = data.get("data", {}).get("viewer", {}).get("searchItems", {})
        total_count = search_items.get("totalCount", 0)
        limit = 10
        skip = response.meta["skip"]
        if skip + limit < total_count:
            skip += limit
            payload = {
                "operationName": "searchDashboardPageLoad",
                "variables": {
                    "text": "electrolyte",
                    "sortBy": "PUBLISHED_DATE_DESC",
                    "skip": skip,
                    "authors": "",
                    "categories": [],
                    "contents": [],
                    "events": [],
                    "publishedDates": [],
                    "subjects": [],
                    "partners": [],
                    "keywords": []
                },
                "query": response.meta["query"]
            }
            yield scrapy.Request(
                url=response.url,
                method="POST",
                body=json.dumps(payload),
                headers=response.request.headers,
                callback=self.parse,
                meta={"skip": skip, "query": response.meta["query"]}
            )